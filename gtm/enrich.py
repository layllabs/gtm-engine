"""Waterfall enrichment, the thing a Clay table does, as config plus code.

For each field an account is missing, try providers in the configured
order until one returns a value or the per-field budget is spent. Every
lookup is logged with provider, cost and outcome so coverage and spend
per provider can be reported, which is how you decide which provider to
drop next quarter.

Providers here are simulated against the account's own data so the demo
runs offline. In production each provider function is an API call behind
the same signature: provider(account) -> value or None.
"""
from __future__ import annotations

from collections.abc import Callable

from .util import CONFIG, domain_of, load_json

Provider = Callable[[dict], str | None]


def _crm(acct: dict, field: str) -> str | None:
    # Simulated: the CRM already knows accounts that came from partner_scan.
    return acct.get(field) if "partner_scan" in acct.get("sources", []) else None


def _maps(acct: dict, field: str) -> str | None:
    if "maps" in acct.get("sources", []):
        return acct.get(field) or None
    return None


def _sos(acct: dict, field: str) -> str | None:
    if field == "owner_name" and "sos_filings" in acct.get("sources", []):
        return acct.get("contact_name") or None
    return None


def _website(acct: dict, field: str) -> str | None:
    if field == "owner_name" and acct.get("website") and acct.get("contact_name"):
        return acct["contact_name"]
    return None


def _apollo(acct: dict, field: str) -> str | None:
    # Simulated: matches on a named contact about 60% of the time, deterministic per account.
    import hashlib
    if not acct.get("contact_name") or field not in ("email", "phone"):
        return None
    h = int(hashlib.md5((acct["account_id"] + field).encode()).hexdigest(), 16) % 100
    if h >= 60:
        return None
    if field == "email":
        first = acct["contact_name"].split(" ")[0].lower().strip(".")
        slug = "".join(c for c in acct["business_name"].lower() if c.isalnum())[:12]
        return f"{first}@{slug}.example"
    return "(555) 555-0100"


def _hunter(acct: dict, field: str) -> str | None:
    return None  # simulated miss; exists to show the waterfall continuing


def _pattern(acct: dict, field: str) -> str | None:
    d = domain_of(acct.get("website", ""))
    first = (acct.get("contact_name") or "").split(" ")[0].lower()
    if field == "email" and d and first and first != "dr.":
        return f"{first}@{d}"
    return None


SIMULATED: dict[str, Callable[[dict, str], str | None]] = {
    "crm": _crm, "maps": _maps, "sos_filings": _sos, "website_scrape": _website,
    "apollo": _apollo, "hunter": _hunter, "pattern_guess": _pattern,
}

FIELD_TO_ACCOUNT_KEY = {"email": "email", "phone": "phone", "owner_name": "contact_name", "review_count": "review_count"}


def enrich(acct: dict, cfg: dict | None = None) -> tuple[dict, list[dict]]:
    """Returns (enriched account copy, lookup log)."""
    cfg = cfg or load_json(CONFIG / "enrichment.json")
    out = dict(acct)
    out.setdefault("field_sources", {})
    log = []
    for field, spec in cfg["fields"].items():
        key = FIELD_TO_ACCOUNT_KEY[field]
        if out.get(key):
            out["field_sources"][field] = out["field_sources"].get(field, "original")
            continue
        spent = 0
        for name in spec["providers"]:
            cost = cfg["providers"][name]["cost_cents"]
            if spent + cost > spec["max_cost_cents"]:
                log.append({"account_id": acct["account_id"], "field": field, "provider": name, "cost_cents": 0, "result": "skipped_budget"})
                continue
            value = SIMULATED[name](acct, field)
            spent += cost
            log.append({"account_id": acct["account_id"], "field": field, "provider": name, "cost_cents": cost,
                        "result": "hit" if value else "miss"})
            if value:
                out[key] = value
                out["field_sources"][field] = name
                if name == "pattern_guess":
                    out["needs_verification"] = True
                if spec["stop_on_first"]:
                    break
    return out, log


def coverage_report(log: list[dict]) -> list[dict]:
    """Hit rate and spend per provider, the table that decides which provider to drop."""
    rows: dict[str, dict] = {}
    for e in log:
        r = rows.setdefault(e["provider"], {"provider": e["provider"], "lookups": 0, "hits": 0, "cost_cents": 0})
        if e["result"] != "skipped_budget":
            r["lookups"] += 1
            r["cost_cents"] += e["cost_cents"]
        if e["result"] == "hit":
            r["hits"] += 1
    for r in rows.values():
        r["hit_rate"] = round(r["hits"] / r["lookups"], 2) if r["lookups"] else 0.0
        r["cost_per_hit_cents"] = round(r["cost_cents"] / r["hits"], 1) if r["hits"] else None
    return sorted(rows.values(), key=lambda r: -r["lookups"])
