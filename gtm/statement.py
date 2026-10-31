"""Statement review: the sales conversation in SMB payments, as a calculator.

Takes a normalized statement (schemas/merchant_statement.schema.json) and
returns what the rep says on the call: effective rate, what is pass-through
versus processor markup, the markup in basis points, what a fair offer
would cost, and the annual difference. Every number comes with the line it
came from so the owner can check it against their own paper.

What it refuses to do: estimate savings when the statement does not
itemize interchange. On tiered or flat-rate pricing the honest answer is
"the markup is hidden; here is the effective rate and here is what we need
to see to go further."
"""
from __future__ import annotations

from datetime import date

# A fair interchange-plus offer for a card-present SMB, as basis points over
# interchange plus a per-item. Config, not a constant, so it can be changed
# per segment without editing code.
DEFAULT_OFFER = {"markup_bps": 20, "per_item": 0.10, "monthly_fixed": 10.00, "pci": 0.00, "equipment": 0.00}

# Thresholds that produce flags. Sources and reasoning in docs/payments/economics.md.
FLAGS = {
    "markup_bps_high": 50,          # processor markup over 50 bps on card-present is high
    "effective_rate_high": 0.030,   # 3.0% effective on card-present is high
    "pci_fee_high": 20.00,          # PCI "non-compliance" fees are often avoidable
    "equipment_lease_high": 30.00,  # leased terminals usually cost more than buying within a year
    "per_item_high": 0.15,
}


def _bps(x: float, volume: float) -> float:
    return round(x / volume * 10000, 1) if volume else 0.0


def review(stmt: dict, offer: dict | None = None, as_of: date | None = None) -> dict:
    offer = {**DEFAULT_OFFER, **(offer or {})}
    f = stmt["fees"]
    vol = stmt["volume"]
    n = stmt["transactions"]
    total = f["total"]
    out: dict = {
        "period": stmt["period"],
        "volume": vol,
        "transactions": n,
        "avg_ticket": round(vol / n, 2) if n else None,
        "effective_rate": round(total / vol, 4) if vol else None,
        "effective_bps": _bps(total, vol),
        "pricing_model": stmt["pricing_model"],
        "lines": [],
        "flags": [],
        "can_estimate_savings": False,
    }

    if stmt["pricing_model"] == "interchange_plus" and f.get("interchange") is not None:
        passthrough = (f.get("interchange") or 0) + (f.get("assessments") or 0)
        markup_dollars = total - passthrough
        pct_markup = f.get("processor_percentage")
        per_item = f.get("processor_per_item")
        out.update({
            "interchange_bps": _bps(f["interchange"], vol),
            "assessments_bps": _bps(f.get("assessments") or 0, vol),
            "passthrough": round(passthrough, 2),
            "markup_total": round(markup_dollars, 2),
            "markup_bps_all_in": _bps(markup_dollars, vol),
            "markup_bps_percentage_only": _bps(pct_markup, vol) if pct_markup is not None else None,
            "per_item_effective": round(per_item / n, 3) if per_item is not None and n else None,
        })
        out["lines"].append(f"Interchange and assessments (pass-through, same at any processor): ${passthrough:,.2f}, {out['interchange_bps'] + out['assessments_bps']:.0f} bps")
        out["lines"].append(f"Everything else is the processor: ${markup_dollars:,.2f}, {out['markup_bps_all_in']:.0f} bps all-in")
        if out["markup_bps_percentage_only"] is not None:
            out["lines"].append(f"Percentage markup alone: {out['markup_bps_percentage_only']:.0f} bps; fair card-present range is roughly 15 to 30")
        if out["per_item_effective"] is not None:
            out["lines"].append(f"Per-item: ${out['per_item_effective']:.3f} per transaction")

        # the offer
        offer_cost = passthrough + vol * offer["markup_bps"] / 10000 + n * offer["per_item"] + offer["monthly_fixed"] + offer["pci"] + offer["equipment"]
        out["offer"] = {**offer, "monthly_cost": round(offer_cost, 2), "effective_rate": round(offer_cost / vol, 4) if vol else None}
        out["monthly_difference"] = round(total - offer_cost, 2)
        out["annual_difference"] = round((total - offer_cost) * 12, 2)
        out["can_estimate_savings"] = True
        out["lines"].append(f"At {offer['markup_bps']} bps + ${offer['per_item']:.2f} with pass-through unchanged: ${offer_cost:,.2f}/mo, difference ${out['monthly_difference']:,.2f}/mo, ${out['annual_difference']:,.2f}/yr")

        if out["markup_bps_all_in"] > FLAGS["markup_bps_high"]:
            out["flags"].append(f"processor markup {out['markup_bps_all_in']:.0f} bps all-in, over {FLAGS['markup_bps_high']}")
        if out["per_item_effective"] and out["per_item_effective"] > FLAGS["per_item_high"]:
            out["flags"].append(f"per-item ${out['per_item_effective']:.2f}, over ${FLAGS['per_item_high']:.2f}")
    else:
        out["lines"].append("Interchange is not itemized on this statement, so the processor's markup is hidden inside the rate.")
        out["lines"].append("Honest next step: ask for an interchange-plus quote or the processor's interchange detail report before promising a number.")
        out["flags"].append(f"pricing model {stmt['pricing_model']}: markup not visible")

    if out["effective_rate"] and out["effective_rate"] > FLAGS["effective_rate_high"]:
        cp = stmt.get("card_present_share")
        if cp is None or cp >= 0.7:
            out["flags"].append(f"effective rate {out['effective_rate']:.2%} on a mostly card-present business, over {FLAGS['effective_rate_high']:.1%}")
    if (f.get("pci") or 0) > FLAGS["pci_fee_high"]:
        out["flags"].append(f"PCI fee ${f['pci']:.2f}/mo; usually avoidable by completing the SAQ")
    if (f.get("equipment") or 0) > FLAGS["equipment_lease_high"]:
        out["flags"].append(f"equipment ${f['equipment']:.2f}/mo; a lease at this rate exceeds purchase price within about a year")

    c = stmt.get("contract") or {}
    if c.get("end_date"):
        end = date.fromisoformat(c["end_date"])
        days = (end - (as_of or date.today())).days
        out["contract"] = {"end_date": c["end_date"], "days_to_end": days, "etf": c.get("early_termination_fee"), "auto_renews": c.get("auto_renews")}
        if c.get("early_termination_fee") and out.get("monthly_difference"):
            months = c["early_termination_fee"] / out["monthly_difference"] if out["monthly_difference"] > 0 else None
            out["contract"]["etf_payback_months"] = round(months, 1) if months else None
            if months:
                out["lines"].append(f"Early termination fee ${c['early_termination_fee']:,.0f} pays back in {months:.1f} months at the difference above")
        if c.get("auto_renews") and days > 0:
            out["lines"].append(f"Contract auto-renews; cancellation window matters: {days} days to {c['end_date']}")
    return out


def summary(r: dict) -> str:
    L = [f"Statement {r['period']}: ${r['volume']:,.0f} on {r['transactions']:,} transactions, avg ticket ${r['avg_ticket']:.2f}",
         f"Effective rate: {r['effective_rate']:.2%} ({r['effective_bps']:.0f} bps), pricing model {r['pricing_model']}", ""]
    L += r["lines"]
    if r["flags"]:
        L += ["", "Flags:"] + [f"  - {x}" for x in r["flags"]]
    return "\n".join(L)
