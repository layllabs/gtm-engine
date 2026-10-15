"""Step 6: classify inbound replies and decide the next move.

Two layers:
  1. These rules: fast, free, deterministic. They handle the obvious
     80% (bounces, out-of-office, unsubscribes) and are the eval baseline.
  2. Claude with prompts/reply-classifier.md for anything the rules mark
     'unknown' or low confidence. Its output must match
     schemas/reply.schema.json or it is rejected.

Order matters: an out-of-office that says 'not interested in spam filters'
is still an out-of-office.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}

RULES: list[tuple[str, str]] = [
    ("bounce", r"mailer-daemon|delivery status notification|550 5\.\d\.\d|address not found|does not exist"),
    ("out_of_office", r"out of (the )?office|\booo\b|on vacation|limited access to email"),
    ("unsubscribe", r"remove me|unsubscribe|stop (emailing|contacting)|take me off"),
    ("wrong_person", r"not the right person|wrong person|handles (the )?(payments|that|this)|reach out to \w+"),
    ("meeting_request", r"\b(monday|tuesday|wednesday|thursday|friday)\b.*\?|\bbook a time\b|\bcalendar link\b|\bcall (me|tomorrow)\b"),
    ("not_now", r"contract until|after the holidays|reach out (then|in|next)|ping me in|not right now|circle back|next (quarter|year)"),
    ("not_interested", r"not interested|already have (a|someone)|we're (all )?set|no thanks"),
    ("question", r"\?"),
    ("interested", r"here (is|are)|attached|sounds good|interested|statement|let's talk|sure\b"),
]

NEXT_ACTION = {
    "bounce": ("suppress", "Mark email invalid, suppress, re-verify the domain list."),
    "out_of_office": ("pause", "Pause sequence, resume the day after they return."),
    "unsubscribe": ("suppress", "Add to suppression list. Do not contact on any channel."),
    "wrong_person": ("reroute", "Create contact for the referred person and send step 1 to them."),
    "meeting_request": ("book", "Confirm the time, send invite, create opportunity."),
    "not_now": ("nurture", "Stop sequence, set follow-up task on the date they gave."),
    "not_interested": ("close", "Stop sequence. Recycle in 180 days if a new signal appears."),
    "question": ("reply", "Draft an answer for approval, keep sequence paused."),
    "interested": ("reply", "Draft reply for approval today, create opportunity."),
    "unknown": ("review", "Send to Claude classifier, then human review."),
}

POSITIVE = {"meeting_request", "interested", "question"}


def classify(body: str) -> tuple[str, float]:
    text = (body or "").lower()
    for label, pattern in RULES:
        if re.search(pattern, text):
            # questions are a weak signal on their own
            return label, 0.6 if label == "question" else 0.9
    return "unknown", 0.0


def _next_month_start(month: int, today: date) -> date:
    year = today.year if month > today.month else today.year + 1
    return date(year, month, 1)


def extract(label: str, body: str, today: date) -> dict:
    text = body or ""
    lower = text.lower()
    info: dict = {}
    if label == "wrong_person":
        if m := re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text):
            info["referred_email"] = m.group(0)
    if label == "out_of_office":
        if m := re.search(r"until (\w+) (\d{1,2})", lower):
            month = MONTHS.get(m.group(1))
            if month:
                ret = date(today.year if month >= today.month else today.year + 1, month, int(m.group(2)))
                info["resume_on"] = (ret + timedelta(days=1)).isoformat()
    if label == "not_now":
        for name, num in MONTHS.items():
            if name in lower:
                info["follow_up_on"] = _next_month_start(num, today).isoformat()
                break
        else:
            if "holidays" in lower:
                info["follow_up_on"] = _next_month_start(1, today).isoformat()
    return info


def process(replies: list[dict], today: date) -> list[dict]:
    out = []
    for r in replies:
        label, conf = classify(r["body"])
        action, note = NEXT_ACTION[label]
        out.append({
            **r,
            "label": label,
            "confidence": conf,
            "positive": label in POSITIVE,
            "next_action": action,
            "note": note,
            "needs_llm": conf < 0.7,
            **extract(label, r["body"], today),
        })
    return out
