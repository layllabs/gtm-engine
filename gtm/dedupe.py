"""Step 2: collapse signals about the same business into one account.

The same shop shows up as 'Rosas Taqueria LLC' in a permit feed and
'Rosa's Taqueria' on maps. Rows are linked if they share ANY key:
phone, website domain, or normalized name + city. Linking is transitive
(union-find), so a Reddit post with no phone still joins the maps listing
through name + city, and the maps listing joins the permit through phone.
"""
from __future__ import annotations

import hashlib

from .util import domain_of, norm_name, phone_digits

# Sources we trust most for contact fields, best first.
SOURCE_PRIORITY = ["maps", "partner_scan", "county_permits", "sos_filings", "craigslist", "reddit"]


def _keys(sig: dict) -> list[str]:
    keys = []
    if p := phone_digits(sig["phone"]):
        keys.append(f"phone:{p}")
    if d := domain_of(sig["website"]):
        keys.append(f"domain:{d}")
    if sig["city"]:
        keys.append(f"name:{norm_name(sig['business_name'])}|{sig['city'].lower()}")
    return keys


def _find(parent: list[int], i: int) -> int:
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def merge(signals: list[dict]) -> list[dict]:
    parent = list(range(len(signals)))
    first_seen: dict[str, int] = {}
    for i, sig in enumerate(signals):
        for k in _keys(sig):
            if k in first_seen:
                a, b = _find(parent, i), _find(parent, first_seen[k])
                if a != b:
                    parent[a] = b
            else:
                first_seen[k] = i

    groups: dict[int, list[dict]] = {}
    for i, sig in enumerate(signals):
        groups.setdefault(_find(parent, i), []).append(sig)

    return [_build_account(rows) for rows in groups.values()]


def _rank(sig: dict) -> int:
    s = sig["source"]
    return SOURCE_PRIORITY.index(s) if s in SOURCE_PRIORITY else len(SOURCE_PRIORITY)


def _build_account(rows: list[dict]) -> dict:
    rows = sorted(rows, key=_rank)

    def pick(field):
        return next((r[field] for r in rows if r[field]), "")

    name = pick("business_name")
    city = pick("city")
    acct_id = "acc_" + hashlib.sha1(f"{norm_name(name)}|{city.lower()}".encode()).hexdigest()[:10]
    reviews = [r["review_count"] for r in rows if r["review_count"] is not None]
    signals = [
        {
            "type": r["signal_type"],
            "date": r["signal_date"],
            "source": r["source"],
            "source_id": r["source_id"],
            "text": r["signal_text"],
        }
        for r in rows
    ]
    return {
        "account_id": acct_id,
        "business_name": name,
        "category": pick("category"),
        "address": pick("address"),
        "city": city,
        "state": pick("state"),
        "zip": pick("zip"),
        "phone": pick("phone"),
        "website": pick("website"),
        "email": pick("email"),
        "contact_name": pick("contact_name"),
        "review_count": max(reviews) if reviews else None,
        "sources": sorted({r["source"] for r in rows}),
        "signals": signals,
        "merged_rows": len(rows),
    }
