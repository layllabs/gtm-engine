"""Step 1: load raw signals from every source into one normalized shape.

In production each source is its own agent (maps search, county permit
portal, state business filings, Reddit/Craigslist scrape, partner scan).
They all write rows in this same shape, so everything downstream is
source-agnostic. The demo reads the same shape from a CSV.
"""
from __future__ import annotations

from pathlib import Path

from .util import parse_date, read_csv, to_int

FIELDS = [
    "source", "source_id", "business_name", "category", "address", "city",
    "state", "zip", "phone", "website", "email", "contact_name",
    "signal_type", "signal_date", "signal_text", "review_count", "rating",
]


def load_signals(path: Path | str) -> list[dict]:
    rows = read_csv(path)
    out = []
    for i, r in enumerate(rows):
        missing = [f for f in ("source", "business_name", "signal_type") if not r.get(f)]
        if missing:
            raise ValueError(f"row {i + 2}: missing required fields {missing}")
        sig = {k: (r.get(k) or "").strip() for k in FIELDS}
        sig["signal_date"] = parse_date(sig["signal_date"])
        sig["review_count"] = to_int(sig["review_count"])
        sig["state"] = sig["state"].upper()
        out.append(sig)
    return out
