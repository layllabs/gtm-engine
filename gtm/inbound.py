"""Inbound speed-to-lead.

A form fill, chat, or inbound call becomes an account in the same shape as
outbound discovery, with attribution attached, then goes through the same
scoring and routing. The difference is urgency: an inbound lead has an SLA
measured in minutes, so this module computes the deadline, picks the owner,
and drafts the first response immediately rather than waiting for the
daily run.

Attribution fields are captured once at intake and never overwritten:
first-touch source, medium, campaign, landing page, referrer.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import territory
from .util import norm_name

SLA_MINUTES = {"hot": 5, "warm": 30, "cold": 240}

HOT_PHRASES = ("switch", "quote", "pricing", "how much", "asap", "today", "this week", "contract ends")


def classify_intent(message: str) -> str:
    m = (message or "").lower()
    if any(p in m for p in HOT_PHRASES):
        return "hot"
    if m.strip():
        return "warm"
    return "cold"


def intake(form: dict, received_at: datetime) -> dict:
    """form keys: business_name, contact_name, email, phone, city, state, zip, category, message,
    utm_source, utm_medium, utm_campaign, landing_page, referrer."""
    intent = classify_intent(form.get("message", ""))
    acct = {
        "account_id": "acc_in_" + norm_name(form["business_name"]).replace(" ", "")[:8],
        "business_name": form["business_name"],
        "contact_name": form.get("contact_name", ""),
        "email": form.get("email", ""),
        "phone": form.get("phone", ""),
        "city": form.get("city", ""),
        "state": form.get("state", ""),
        "zip": form.get("zip", ""),
        "category": form.get("category", ""),
        "lane": "direct",
        "sources": ["inbound"],
        "signals": [{"type": "inbound_request", "date": received_at.date(), "source": "inbound", "source_id": form.get("id", ""), "text": form.get("message", "")}],
        "attribution": {
            "first_touch_source": form.get("utm_source") or ("referral" if form.get("referrer") else "direct"),
            "first_touch_medium": form.get("utm_medium", ""),
            "first_touch_campaign": form.get("utm_campaign", ""),
            "landing_page": form.get("landing_page", ""),
            "referrer": form.get("referrer", ""),
            "captured_at": received_at.isoformat(timespec="minutes"),
        },
        "intent": intent,
    }
    owner, rule = territory.assign(acct)
    acct["owner"] = owner
    acct["territory_rule"] = rule
    acct["sla_minutes"] = SLA_MINUTES[intent]
    acct["respond_by"] = (received_at + timedelta(minutes=SLA_MINUTES[intent])).isoformat(timespec="minutes")
    acct["first_response"] = draft_first_response(acct)
    return acct


def draft_first_response(acct: dict) -> str:
    first = (acct.get("contact_name") or "there").split(" ")[0]
    if acct["intent"] == "hot":
        return (f"Hi {first}, thanks for reaching out about {acct['business_name']}. Fastest way for me to give you a real number "
                f"is one recent processing statement; reply with a photo of page one and I'll send back what you're paying and what it should be, today. "
                f"Or if you'd rather talk, what's a good number and time?")
    return (f"Hi {first}, thanks for the note about {acct['business_name']}. Happy to help. If you send one recent statement I can show you "
            f"line by line where the fees are. No pitch until you've seen the math.")


def sla_status(acct: dict, now: datetime) -> str:
    deadline = datetime.fromisoformat(acct["respond_by"])
    if now <= deadline:
        return "on_time"
    return "breached"
