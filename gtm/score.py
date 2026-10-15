"""Step 3: score each account against every ICP and keep the best fit.

score = sum(weight[c] * component[c]) for five components, each 0..1:

  category_fit     1.0 if the category is in the ICP, otherwise disqualified
  signal_strength  strongest signal, +0.1 per extra distinct signal type (cap 1.0)
  recency          0.5 ** (age_days / half_life) of the strongest signal
  reachability     email .5 + phone .3 + address .1 + named contact .1
  size_proxy       review count on a log scale between floor and ceiling

Weights live in config/icp/*.json so the scoring model can change without
touching code. Every score ships with plain-English reasons so a rep (or
an agent) can see WHY an account is tier A.
"""
from __future__ import annotations

import math
from datetime import date
from pathlib import Path

from .util import CONFIG, load_json


def load_icps(directory: Path | None = None) -> list[dict]:
    directory = directory or CONFIG / "icp"
    return [load_json(p) for p in sorted(directory.glob("*.json"))]


def _best_signal(acct: dict, icp: dict) -> dict | None:
    strength = icp["signal_strength"]
    ranked = sorted(
        acct["signals"],
        key=lambda s: (strength.get(s["type"], 0.0), s["date"] or date.min),
        reverse=True,
    )
    return ranked[0] if ranked else None


def _components(acct: dict, icp: dict, as_of: date) -> tuple[dict, list[str]]:
    reasons = []
    strength_map = icp["signal_strength"]

    best = _best_signal(acct, icp)
    base = strength_map.get(best["type"], 0.1) if best else 0.0
    distinct = {s["type"] for s in acct["signals"] if s["type"] != "listing_only"}
    stack_bonus = 0.1 * max(0, len(distinct) - 1)
    signal_strength = min(1.0, base + stack_bonus)

    age = (as_of - best["date"]).days if best and best["date"] else 365
    age = max(age, 0)
    recency = 0.5 ** (age / icp["recency_half_life_days"])
    if not best or best["type"] == "listing_only":
        recency = 0.1  # a listing is not an event; nothing happened recently
    if best and best["type"] != "listing_only":
        reasons.append(f"{best['type']} {age}d ago ({best['source']})")
    if len(distinct) > 1:
        reasons.append(f"stacked signals: {', '.join(sorted(distinct))}")

    reach = 0.0
    found = []
    for field, pts in (("email", 0.5), ("phone", 0.3), ("address", 0.1), ("contact_name", 0.1)):
        if acct[field]:
            reach += pts
            found.append(field)
    if acct["email"]:
        reasons.append("direct email found")
    elif acct["phone"]:
        reasons.append("phone only, no email")

    sp = icp["size_proxy"]
    rc = acct["review_count"]
    if rc is None:
        size = 0.3
    elif rc < sp["review_count_floor"]:
        size = 0.1
        reasons.append(f"small footprint ({rc} reviews)")
    else:
        lo, hi = math.log(sp["review_count_floor"]), math.log(sp["review_count_ceiling"])
        size = min(1.0, (math.log(rc) - lo) / (hi - lo))

    comps = {
        "category_fit": 1.0,
        "signal_strength": round(signal_strength, 3),
        "recency": round(recency, 3),
        "reachability": round(reach, 3),
        "size_proxy": round(size, 3),
    }
    return comps, reasons


def _tier(score: float, tiers: dict) -> str:
    for name in ("A", "B", "C"):
        if score >= tiers[name]:
            return name
    return "D"


def score_account(acct: dict, icps: list[dict], as_of: date) -> dict:
    """Returns the account with icp, lane, score, tier, components, reasons."""
    for icp in icps:
        if acct["category"] in icp["exclude_categories"]:
            return {**acct, "icp": icp["id"], "lane": icp["lane"], "score": 0, "tier": "DQ",
                    "components": {}, "reasons": [f"excluded category: {acct['category']}"]}

    fits = [i for i in icps if acct["category"] in i["include_categories"]]
    if not fits:
        return {**acct, "icp": None, "lane": None, "score": 0, "tier": "DQ",
                "components": {}, "reasons": [f"no ICP covers category: {acct['category']}"]}

    best = None
    for icp in fits:
        if icp["geo"]["states"] and acct["state"] not in icp["geo"]["states"]:
            cand = {**acct, "icp": icp["id"], "lane": icp["lane"], "score": 0, "tier": "DQ",
                    "components": {}, "reasons": [f"out of territory: {acct['state'] or 'unknown'}"]}
        else:
            comps, reasons = _components(acct, icp, as_of)
            total = round(sum(icp["weights"][k] * v for k, v in comps.items()), 1)
            cand = {**acct, "icp": icp["id"], "lane": icp["lane"], "score": total,
                    "tier": _tier(total, icp["tiers"]), "components": comps, "reasons": reasons}
        if best is None or cand["score"] > best["score"]:
            best = cand
    return best


def score_all(accounts: list[dict], icps: list[dict], as_of: date) -> list[dict]:
    scored = [score_account(a, icps, as_of) for a in accounts]
    return sorted(scored, key=lambda a: a["score"], reverse=True)
