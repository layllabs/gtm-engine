"""The full engine run, end to end. Each step is a function in its own
module so any single step can be swapped for an agent or an API call
without touching the others."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import copywriting, dedupe, discover, health, replies, report, route, score, store
from .lifecycle import ACTION_TO_STATE, REPLY_TO_STATE, InvalidTransition, Ledger
from .util import CONFIG, load_json, read_jsonl, write_csv, write_jsonl


def run(data_dir: Path, out_dir: Path, as_of: date) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    sender = load_json(CONFIG / "sender.json")["sender_name"]
    stamp = f"{as_of.isoformat()}T08:00"
    ledger = Ledger()

    # 1. discover
    signals = discover.load_signals(data_dir / "raw_signals.csv")

    # 2. dedupe
    accounts = dedupe.merge(signals)

    # 3. score
    scored = score.score_all(accounts, score.load_icps(), as_of)
    for a in scored:
        if a["tier"] == "DQ":
            ledger.move(a["account_id"], "disqualified", a["reasons"][0], stamp)
        else:
            ledger.move(a["account_id"], "scored", f"{a['icp']} score {a['score']} tier {a['tier']}", stamp)

    # 4. route
    sup = route.load_suppression(data_dir / "suppression.csv")
    routed = route.route_all(scored, sup, as_of)
    for a in routed:
        target = ACTION_TO_STATE[a["action"]]
        current = ledger.state[a["account_id"]]
        if current != "disqualified" and current != target:
            ledger.move(a["account_id"], target, f"rule {a['route_rule']}", stamp)

    # 5. copy + lint gate
    sequences = copywriting.load_sequences()
    drafts, blocked = [], []
    for a in routed:
        if not a["sequence"]:
            continue
        rendered = copywriting.render(a, sequences[a["sequence"]], sender)
        drafts.extend(rendered)
        if any(d["lint"] for d in rendered):
            blocked.append(a["account_id"])
        else:
            ledger.move(a["account_id"], "sequenced", f"{a['sequence']} enrolled, lint clean", stamp)

    # 6. replies
    by_email = {a["email"].lower(): a for a in routed if a["email"]}
    classified = replies.process(read_jsonl(data_dir / "replies.jsonl"), as_of)
    for r in classified:
        acct = by_email.get(r["from"].lower())
        r["account_id"] = acct["account_id"] if acct else None
        r["business_name"] = acct["business_name"] if acct else None
        if not acct:
            r["applied"] = "unmatched sender, matched later by message id"
            continue
        at = r["received"][:16]
        try:
            ledger.move(acct["account_id"], REPLY_TO_STATE[r["label"]], f"reply {r['id']}: {r['label']}", at)
            if r["label"] == "meeting_request":
                ledger.move(acct["account_id"], "meeting", "meeting requested in reply", at)
            if r["label"] == "wrong_person":
                ledger.move(acct["account_id"], "rerouted", f"referred to {r.get('referred_email')}", at)
            r["applied"] = f"-> {ledger.state[acct['account_id']]}"
        except InvalidTransition as e:
            r["applied"] = f"skipped: {e}"

    # 7. health
    stats = load_json(data_dir / "mailbox_stats.json")
    mailboxes, domains = health.check_mailboxes(stats)
    variants = health.check_variants(stats)
    template_lint = copywriting.lint_templates(sequences, sender)

    # write everything
    write_csv(out_dir / "accounts_scored.csv", [
        {**a, "reasons": "; ".join(a["reasons"]), "sources": "+".join(a["sources"]),
         "state_now": ledger.state[a["account_id"]],
         "task": f"{a['task']['type']} by {a['task']['due']}" if a["task"] else ""}
        for a in routed
    ], ["account_id", "business_name", "category", "city", "state", "icp", "lane", "score", "tier",
        "action", "sequence", "task", "state_now", "reasons", "sources", "merged_rows", "suppression_reason"])
    write_jsonl(out_dir / "drafts.jsonl", drafts)
    write_csv(out_dir / "replies_classified.csv", classified,
              ["id", "business_name", "label", "confidence", "next_action", "applied",
               "follow_up_on", "resume_on", "referred_email", "needs_llm", "body"])
    write_jsonl(out_dir / "events.jsonl", ledger.events)
    store.write(out_dir / "engine.db", routed, drafts, classified, ledger.state, ledger.events)

    result = {
        "as_of": as_of.isoformat(),
        "signals": len(signals),
        "accounts": routed,
        "drafts": drafts,
        "blocked": blocked,
        "replies": classified,
        "mailboxes": mailboxes,
        "domains": domains,
        "variants": variants,
        "template_lint": template_lint,
        "states": ledger.state,
        "events": ledger.events,
    }
    (out_dir / "scoreboard.md").write_text(report.scoreboard(result), encoding="utf-8")
    (out_dir / "drafts.md").write_text(report.drafts_md(drafts, routed), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(report.summary(result), indent=2), encoding="utf-8")
    return result
