"""CLI.

  python -m gtm run                 full engine run on sample data
  python -m gtm run --as-of today   use today's date for recency
  python -m gtm lint-copy           lint every sequence template, exit 1 on issues
  python -m gtm eval-replies        rules classifier vs labeled replies
  python -m gtm health              deliverability check only
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import copywriting, health, pipeline
from .util import CONFIG, ROOT, load_json


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="gtm", description="Signal-based outbound engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="discover > dedupe > score > route > copy > replies > health")
    r.add_argument("--data", default=str(ROOT / "data" / "sample"))
    r.add_argument("--out", default=str(ROOT / "examples" / "output"))
    r.add_argument("--as-of", default=load_json(CONFIG / "sender.json")["as_of_default"],
                   help="YYYY-MM-DD or 'today'. Pinned by default so the demo output is reproducible.")

    sub.add_parser("lint-copy", help="lint all sequence templates")

    e = sub.add_parser("eval-replies", help="score the rules classifier against the labeled reply set")
    e.add_argument("--set", default=str(ROOT / "data" / "sample" / "reply_eval.jsonl"))

    h = sub.add_parser("health", help="deliverability check")
    h.add_argument("--stats", default=str(ROOT / "data" / "sample" / "mailbox_stats.json"))

    args = p.parse_args(argv)

    if args.cmd == "run":
        as_of = date.today() if args.as_of == "today" else date.fromisoformat(args.as_of)
        res = pipeline.run(Path(args.data), Path(args.out), as_of)
        s = __import__("gtm.report", fromlist=["summary"]).summary(res)
        print(f"engine run {s['as_of']}: {s['raw_signals']} signals -> {s['accounts_after_dedupe']} accounts")
        print(f"  tiers    {s['tiers']}")
        print(f"  actions  {s['actions']}")
        print(f"  drafts   {s['drafts']} ({s['drafts_failing_lint']} failing lint)")
        print(f"  replies  {s['replies']}")
        print(f"  inboxes  {s['mailboxes']}  retire: {s['domains_to_retire'] or 'none'}")
        print(f"  wrote    {args.out}/scoreboard.md")
        return 0

    if args.cmd == "lint-copy":
        sender = load_json(CONFIG / "sender.json")["sender_name"]
        results = copywriting.lint_templates(copywriting.load_sequences(), sender)
        bad = [x for x in results if x["issues"]]
        for x in bad:
            print(f"FAIL {x['sequence']} day {x['day']} {x['variant']} opener={x['opener']}: {'; '.join(x['issues'])}")
        print(f"{len(results)} combinations checked, {len(bad)} failing")
        return 1 if bad else 0

    if args.cmd == "eval-replies":
        from .replies import classify
        from .util import read_jsonl
        rows = read_jsonl(args.set)
        misses = [(r["label"], classify(r["body"])[0], r["body"]) for r in rows
                  if classify(r["body"])[0] != r["label"]]
        for want, got, body in misses:
            print(f"MISS want={want} got={got} | {body[:80]}")
        acc = (len(rows) - len(misses)) / len(rows)
        print(f"{len(rows) - len(misses)}/{len(rows)} correct ({acc:.0%}). "
              "Every miss here is a case the LLM classifier has to carry.")
        return 1 if acc < 0.9 else 0

    if args.cmd == "health":
        stats = load_json(args.stats)
        boxes, domains = health.check_mailboxes(stats)
        for b in boxes:
            print(f"{b['id']:7} {b['domain']:22} {b['status']:8} {'; '.join(b['reasons'])}")
        for d in domains:
            print(f"domain {d['domain']}: {d['verdict']}")
        return 1 if any(b["status"] == "pause" for b in boxes) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
