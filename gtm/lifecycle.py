"""Account lifecycle as an explicit state machine.

Every state change is validated against TRANSITIONS and written to an
append-only event log, so the CRM can always answer 'how did this
account get here?'. docs/crm/lifecycle.md has the same machine as a
Mermaid diagram; tests/test_engine.py keeps the two in sync.
"""
from __future__ import annotations

TRANSITIONS: dict[str, set[str]] = {
    "new": {"scored", "disqualified"},
    "scored": {"queued", "task_pending", "nurture", "suppressed", "disqualified"},
    "task_pending": {"queued", "engaged", "nurture", "disqualified"},
    "queued": {"sequenced", "suppressed"},
    "sequenced": {"engaged", "paused", "nurture", "closed_no", "suppressed"},
    "paused": {"sequenced", "suppressed"},
    "engaged": {"meeting", "nurture", "closed_no", "suppressed", "rerouted"},
    "rerouted": {"queued"},
    "meeting": {"opportunity", "nurture", "closed_no"},
    "opportunity": {"won", "lost"},
    "nurture": {"scored"},
    "closed_no": {"scored"},
    "lost": {"scored"},
    "won": set(),
    "suppressed": set(),
    "disqualified": {"scored"},
}

ACTION_TO_STATE = {
    "sequence": "queued",
    "sequence_and_call": "queued",
    "visit_and_sequence": "queued",
    "call_first": "task_pending",
    "nurture": "nurture",
    "suppress": "suppressed",
    "disqualify": "disqualified",
}

REPLY_TO_STATE = {
    "interested": "engaged",
    "question": "engaged",
    "meeting_request": "engaged",
    "not_now": "nurture",
    "not_interested": "closed_no",
    "unsubscribe": "suppressed",
    "bounce": "suppressed",
    "out_of_office": "paused",
    "wrong_person": "engaged",
}


class InvalidTransition(ValueError):
    pass


class Ledger:
    def __init__(self):
        self.state: dict[str, str] = {}
        self.events: list[dict] = []

    def move(self, account_id: str, to: str, reason: str, at: str) -> None:
        current = self.state.get(account_id, "new")
        if to not in TRANSITIONS[current]:
            raise InvalidTransition(f"{account_id}: {current} -> {to} is not allowed")
        self.state[account_id] = to
        self.events.append({"at": at, "account_id": account_id, "from": current, "to": to, "reason": reason})
