"""Shadow CRM in SQLite.

The system of record (Salesforce/HubSpot/Attio) stays the source of truth
for pipeline. This local database holds what the CRM can't flexibly hold:
raw signals, score components, copy variants, reply labels, and the full
lifecycle event log. Schema mirrors docs/crm/data-model.md.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE accounts (
  account_id TEXT PRIMARY KEY, business_name TEXT, category TEXT, city TEXT, state TEXT,
  phone TEXT, website TEXT, email TEXT, contact_name TEXT, review_count INTEGER,
  icp TEXT, lane TEXT, score REAL, tier TEXT, components TEXT, reasons TEXT,
  state_current TEXT, sources TEXT, owner TEXT, territory_rule TEXT
);
CREATE TABLE signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_id TEXT REFERENCES accounts(account_id),
  type TEXT, date TEXT, source TEXT, source_id TEXT, text TEXT
);
CREATE TABLE routes (
  account_id TEXT PRIMARY KEY REFERENCES accounts(account_id),
  rule TEXT, action TEXT, sequence TEXT, task TEXT, suppression_reason TEXT
);
CREATE TABLE touches (
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_id TEXT REFERENCES accounts(account_id),
  sequence TEXT, variant TEXT, day INTEGER, channel TEXT, subject TEXT, body TEXT, lint TEXT
);
CREATE TABLE replies (
  id TEXT PRIMARY KEY, account_id TEXT, from_addr TEXT, sequence TEXT, variant TEXT,
  received TEXT, body TEXT, label TEXT, confidence REAL, next_action TEXT, extra TEXT
);
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, account_id TEXT, from_state TEXT, to_state TEXT, reason TEXT
);
"""


def write(db_path: Path, routed: list[dict], drafts: list[dict], replies: list[dict],
          ledger_state: dict, events: list[dict]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    for a in routed:
        con.execute(
            "INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["account_id"], a["business_name"], a["category"], a["city"], a["state"], a["phone"],
             a["website"], a["email"], a["contact_name"], a["review_count"], a["icp"], a["lane"],
             a["score"], a["tier"], json.dumps(a["components"]), json.dumps(a["reasons"]),
             ledger_state.get(a["account_id"]), json.dumps(a["sources"]), a.get("owner"), a.get("territory_rule")),
        )
        for s in a["signals"]:
            con.execute(
                "INSERT INTO signals (account_id,type,date,source,source_id,text) VALUES (?,?,?,?,?,?)",
                (a["account_id"], s["type"], str(s["date"]), s["source"], s["source_id"], s["text"]),
            )
        con.execute(
            "INSERT INTO routes VALUES (?,?,?,?,?,?)",
            (a["account_id"], a["route_rule"], a["action"], a["sequence"],
             json.dumps(a["task"]) if a["task"] else None, a["suppression_reason"]),
        )
    for d in drafts:
        con.execute(
            "INSERT INTO touches (account_id,sequence,variant,day,channel,subject,body,lint) VALUES (?,?,?,?,?,?,?,?)",
            (d["account_id"], d["sequence"], d["variant"], d["day"], d["channel"], d["subject"],
             d["body"], json.dumps(d["lint"])),
        )
    core = {"id", "account_id", "from", "sequence", "variant", "received", "body", "label", "confidence", "next_action"}
    for r in replies:
        con.execute(
            "INSERT INTO replies VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (r["id"], r.get("account_id"), r["from"], r["sequence"], r["variant"], r["received"],
             r["body"], r["label"], r["confidence"], r["next_action"],
             json.dumps({k: v for k, v in r.items() if k not in core})),
        )
    for e in events:
        con.execute(
            "INSERT INTO events (at,account_id,from_state,to_state,reason) VALUES (?,?,?,?,?)",
            (e["at"], e["account_id"], e["from"], e["to"], e["reason"]),
        )
    con.commit()
    con.close()
