"""Territory assignment: which rep owns an account.

Config in config/territories.json. Deterministic round-robin uses the
account id hash so reruns never reassign. The equivalent in a sales stack
is the LeanData or Chili Piper routing graph; here it is a table so the
assignment logic can be diffed in a pull request.
"""
from __future__ import annotations

import hashlib

from .util import CONFIG, load_json


def _matches(match: dict, acct: dict) -> bool:
    if "zip_prefix" in match:
        z = (acct.get("zip") or "")[:3]
        if not z or z not in match["zip_prefix"]:
            return False
    if "state" in match and acct.get("state") not in match["state"]:
        return False
    if "city" in match and (acct.get("city") or "").lower() not in [c.lower() for c in match["city"]]:
        return False
    return True


def assign(acct: dict, cfg: dict | None = None) -> tuple[str | None, str]:
    """Returns (owner, rule_name)."""
    cfg = cfg or load_json(CONFIG / "territories.json")
    if acct.get("lane") == "partner" and cfg.get("partner_lane_override"):
        return cfg["partner_lane_override"], "partner-lane-override"
    if acct.get("lane") == "enterprise" and cfg.get("enterprise_lane_override"):
        return cfg["enterprise_lane_override"], "enterprise-lane-override"
    for rule in cfg["rules"]:
        if _matches(rule["match"], acct):
            owner = rule["owner"]
            if isinstance(owner, dict) and "round_robin" in owner:
                pool = owner["round_robin"]
                idx = int(hashlib.md5(acct["account_id"].encode()).hexdigest(), 16) % len(pool)
                return pool[idx], rule["name"]
            return owner, rule["name"]
    return None, "no-rule"
