"""Step 4: decide the next action for every scored account.

Rules come from config/routing.json and are evaluated top to bottom; the
first match wins. Suppression (unsubscribes, existing customers, do-not-
contact) is checked before anything else so nobody gets emailed twice
after asking us to stop.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from .util import CONFIG, domain_of, load_json, phone_digits, read_csv


def load_suppression(path: Path | str) -> dict[str, set[str]]:
    out = {"email": set(), "domain": set(), "phone": set()}
    for r in read_csv(path):
        t, v = r["type"].strip(), r["value"].strip().lower()
        if t == "phone":
            v = phone_digits(v)
        if t in out and v:
            out[t].add(v)
    return out


def suppression_hit(acct: dict, sup: dict[str, set[str]]) -> str | None:
    if acct["email"] and acct["email"].lower() in sup["email"]:
        return "email on suppression list"
    for d in {domain_of(acct["website"]), domain_of(acct["email"])}:
        if d and d in sup["domain"]:
            return f"domain {d} on suppression list"
    p = phone_digits(acct["phone"])
    if p and p in sup["phone"]:
        return "phone on do-not-contact list"
    return None


def _matches(when: dict, facts: dict) -> bool:
    for key, expected in when.items():
        actual = facts.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def route_all(scored: list[dict], sup: dict, as_of: date, rules_path: Path | None = None) -> list[dict]:
    rules = load_json(rules_path or CONFIG / "routing.json")["rules"]
    start = datetime.combine(as_of, datetime.min.time()).replace(hour=8)
    out = []
    for acct in scored:
        hit = suppression_hit(acct, sup)
        facts = {
            "suppressed": bool(hit),
            "lane": acct["lane"],
            "tier": acct["tier"],
            # a pattern-guessed email counts as no email until verified
            "has_email": bool(acct["email"]) and not acct.get("needs_verification"),
            "has_phone": bool(acct["phone"]),
            "has_address": bool(acct["address"]),
        }
        rule = next(r for r in rules if _matches(r["when"], facts))
        task = None
        if rule["task"]:
            task = {
                **rule["task"],
                "due": (start + timedelta(hours=rule["task"]["due_hours"])).isoformat(timespec="minutes"),
            }
        out.append({
            **acct,
            "route_rule": rule["name"],
            "action": rule["action"],
            "sequence": rule["sequence"],
            "task": task,
            "suppression_reason": hit,
        })
    return out
