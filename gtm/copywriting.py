"""Step 5: render personalized drafts and lint them before anything sends.

Personalization is driven by the signal that put the account in the queue:
a permit gets a permit opener, a fee complaint gets a fee opener. In
production Claude writes a custom first line on top of this and a second
model QA-reviews it (see prompts/). The template opener here is the
deterministic fallback, so a draft always exists even if the model is down.

The linter is the gate. A draft that fails lint never gets enrolled.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .util import CONFIG, clean_business_name, load_json

CATEGORY_NOUN = {
    "restaurant": "restaurant", "cafe": "coffee shop", "bakery": "bakery",
    "auto_repair": "auto shop", "salon": "salon", "barbershop": "barbershop",
    "retail": "shop", "dry_cleaner": "dry cleaner", "food_truck": "food truck",
    "veterinary": "clinic",
    "ecommerce": "online store", "marketplace": "marketplace", "travel": "travel company",
    "digital_goods": "digital business", "subscription_saas": "software company", "mobility": "mobility company", "gaming": "gaming company",
}
CUSTOMER_NOUN = {
    "restaurant_supply": "restaurant owners", "pos_reseller": "merchants",
    "bookkeeper": "small business owners", "commercial_landlord": "tenants",
    "business_association": "local business owners", "equipment_repair": "restaurant owners",
}
SPAM_PHRASES = [
    "act now", "risk-free", "risk free", "guarantee", "click here", "100%",
    "limited time", "free money", "no obligation", "!!",
]
VAR = re.compile(r"{{\s*(\w+)\s*}}")


def load_sequences(directory: Path | None = None) -> dict[str, dict]:
    directory = directory or CONFIG / "sequences"
    return {s["id"]: s for s in (load_json(p) for p in sorted(directory.glob("*.json")))}


def first_name(contact: str) -> str:
    parts = (contact or "").replace(".", "").split()
    if not parts:
        return "there"
    if parts[0].lower() == "dr" and len(parts) > 1:
        return f"Dr. {parts[-1]}"
    return parts[0]


def assign_variant(account_id: str, seq: dict) -> str:
    """Stable A/B split: same account always gets the same variant."""
    variants = sorted({s["variant"] for s in seq["steps"] if s["day"] == 0})
    h = int(hashlib.md5(account_id.encode()).hexdigest(), 16)
    return variants[h % len(variants)]


def fill(text: str, values: dict) -> str:
    return VAR.sub(lambda m: str(values.get(m.group(1), m.group(0))), text or "")


def build_values(acct: dict, seq: dict, sender_name: str) -> dict:
    values = {
        "first_name": first_name(acct["contact_name"]),
        "business_name": clean_business_name(acct["business_name"]),
        "city": acct["city"] or "your area",
        "category_noun": CATEGORY_NOUN.get(acct["category"], "business"),
        "customer_noun": CUSTOMER_NOUN.get(acct["category"], "business owners"),
        "sender_name": sender_name,
    }
    strength_types = list(seq["openers"].keys())
    acct_types = [s["type"] for s in acct["signals"]]
    # opener for the strongest signal we have a line for (openers are listed strongest first)
    chosen = next((t for t in strength_types if t in acct_types), "listing_only")
    values["signal_line"] = fill(seq["openers"][chosen], values)
    values["_opener_used"] = chosen
    return values


def render(acct: dict, seq: dict, sender_name: str) -> list[dict]:
    values = build_values(acct, seq, sender_name)
    variant = assign_variant(acct["account_id"], seq)
    drafts = []
    for step in seq["steps"]:
        if step["day"] == 0 and step["variant"] != variant:
            continue
        subject = fill(step["subject"], values) if step["subject"] else None
        body = fill(step["body"], values)
        drafts.append({
            "account_id": acct["account_id"],
            "business_name": acct["business_name"],
            "to": acct["email"] if step["channel"] == "email" else acct["phone"],
            "sequence": seq["id"],
            "variant": variant,
            "day": step["day"],
            "channel": step["channel"],
            "opener": values["_opener_used"],
            "subject": subject,
            "body": body,
            "lint": lint(subject, body, seq["constraints"]) if step["channel"] == "email" else [],
        })
    return drafts


def lint(subject: str | None, body: str, constraints: dict) -> list[str]:
    """Returns a list of problems. Empty list means the draft can send."""
    issues = []
    text = f"{subject or ''}\n{body}"
    if "\u2014" in text or "\u2013" in text:  # em dash, en dash
        issues.append("contains an em/en dash (reads as machine-written)")
    if leftover := VAR.findall(text):
        issues.append(f"unfilled variables: {sorted(set(leftover))}")
    words = len(re.findall(r"\b[\w']+\b", body))
    if words > constraints["max_words"]:
        issues.append(f"{words} words (max {constraints['max_words']})")
    links = len(re.findall(r"https?://|www\.", body))
    if links > constraints["max_links"]:
        issues.append(f"{links} links (max {constraints['max_links']})")
    questions = body.count("?")
    if questions > constraints["max_questions"]:
        issues.append(f"{questions} questions (max {constraints['max_questions']})")
    lower = text.lower()
    for phrase in SPAM_PHRASES:
        if phrase in lower:
            issues.append(f"spam trigger: '{phrase}'")
    if subject:
        if len(subject) > 45:
            issues.append(f"subject is {len(subject)} chars (max 45)")
        if re.search(r"\b[A-Z]{4,}\b", subject):
            issues.append("subject has ALL CAPS word")
    return issues


def lint_templates(sequences: dict[str, dict], sender_name: str = "Sam") -> list[dict]:
    """Render every opener x every email step with a worst-case long name and lint it."""
    results = []
    fake = {
        "account_id": "acc_lint", "business_name": "Westside Family Restaurant & Bakery",
        "category": "restaurant", "city": "Rancho Cucamonga", "contact_name": "Alexandra Montgomery",
        "email": "x@example.com", "phone": "", "signals": [],
    }
    for seq in sequences.values():
        for opener in seq["openers"]:
            acct = {**fake, "signals": [{"type": opener}]}
            values = build_values(acct, seq, sender_name)
            for step in seq["steps"]:
                if step["channel"] != "email":
                    continue
                subject = fill(step["subject"], values)
                body = fill(step["body"], values)
                results.append({
                    "sequence": seq["id"], "opener": opener, "day": step["day"],
                    "variant": step["variant"], "issues": lint(subject, body, seq["constraints"]),
                })
    return results
