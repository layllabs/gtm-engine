"""Step 7: deliverability health check, run before every send day.

Mailbox status is one of:
  ok       in rotation
  watch    in rotation, flagged in the scoreboard
  pause    pulled from rotation today
  warming  not sending cold yet (too new or reputation too low)

Domain rule: two paused mailboxes on one domain means retire the domain.
Variant check: two-proportion z-test so we don't crown a winner on noise.
"""
from __future__ import annotations

import math

from .util import CONFIG, load_json


def _status(rate: float, line: dict) -> str:
    if rate >= line["pause"]:
        return "pause"
    if rate >= line["watch"]:
        return "watch"
    return "ok"


def check_mailboxes(stats: dict, rules: dict | None = None) -> tuple[list[dict], list[dict]]:
    rules = rules or load_json(CONFIG / "deliverability.json")
    rows = []
    for m in stats["mailboxes"]:
        row = {**m, "bounce_rate": None, "complaint_rate": None, "reasons": []}
        if m["warmup_days"] < rules["min_warmup_days"] or m["warmup_reputation"] < rules["min_warmup_reputation"]:
            row["status"] = "warming"
            row["reasons"].append(f"warmup {m['warmup_days']}d, reputation {m['warmup_reputation']:.0%}")
            rows.append(row)
            continue
        sent = m["sent_7d"]
        if sent < rules["min_sample_for_rates"]:
            row["status"] = "ok"
            row["reasons"].append(f"only {sent} sends, rates not meaningful yet")
            rows.append(row)
            continue
        br = m["bounced_7d"] / sent
        cr = m["spam_complaints_7d"] / sent
        row["bounce_rate"], row["complaint_rate"] = round(br, 4), round(cr, 4)
        statuses = [_status(br, rules["bounce_rate"]), _status(cr, rules["spam_complaint_rate"])]
        if br >= rules["bounce_rate"]["watch"]:
            row["reasons"].append(f"bounce {br:.2%}")
        if cr >= rules["spam_complaint_rate"]["watch"]:
            row["reasons"].append(f"complaints {cr:.2%}")
        row["status"] = "pause" if "pause" in statuses else "watch" if "watch" in statuses else "ok"
        rows.append(row)

    domains: dict[str, list[dict]] = {}
    for r in rows:
        domains.setdefault(r["domain"], []).append(r)
    domain_rows = []
    for d, boxes in sorted(domains.items()):
        paused = sum(1 for b in boxes if b["status"] == "pause")
        domain_rows.append({
            "domain": d,
            "mailboxes": len(boxes),
            "paused": paused,
            "verdict": "retire and replace" if paused >= 2 else "keep",
        })
    return rows, domain_rows


def two_proportion_z(x1: int, n1: int, x2: int, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return 0.0
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 0.0 if se == 0 else ((x1 / n1) - (x2 / n2)) / se


def check_variants(stats: dict, rules: dict | None = None) -> list[dict]:
    rules = rules or load_json(CONFIG / "deliverability.json")
    by_seq: dict[str, list[dict]] = {}
    for v in stats["variants"]:
        by_seq.setdefault(v["sequence"], []).append(v)
    out = []
    for seq, variants in sorted(by_seq.items()):
        for v in variants:
            rr = v["replies"] / v["sent"] if v["sent"] else 0
            out.append({
                "sequence": seq, "variant": v["variant"], "sent": v["sent"],
                "reply_rate": round(rr, 4), "positive_rate": round(v["positive"] / v["sent"], 4) if v["sent"] else 0,
                "flag": "below reply floor" if rr < rules["reply_rate_floor_per_variant"] else "",
                "verdict": "",
            })
        if len(variants) == 2:
            a, b = variants
            z = two_proportion_z(a["positive"], a["sent"], b["positive"], b["sent"])
            leader = a["variant"] if z > 0 else b["variant"]
            verdict = (f"{leader} leads on positive replies, z={z:.2f}: "
                       + ("significant, promote it" if abs(z) >= 1.96 else "not significant yet, keep testing"))
            for row in out:
                if row["sequence"] == seq:
                    row["verdict"] = verdict
    return out
