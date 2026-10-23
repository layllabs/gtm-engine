"""Export the reply classifier rules to docs/rules.json so the browser
playground on the portfolio site runs the exact same regexes as the
Python engine. A test fails if the two drift. Run after editing
gtm/replies.py:

    python scripts/export_rules.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gtm.replies import NEXT_ACTION, POSITIVE, RULES  # noqa: E402

OUT = ROOT / "docs" / "rules.json"


def build() -> dict:
    return {
        "source": "gtm/replies.py",
        "note": "Evaluated top to bottom, first match wins, case-insensitive. 'question' gets 0.6 confidence, everything else 0.9, no match is 'unknown' at 0.0.",
        "rules": [{"label": label, "pattern": pattern} for label, pattern in RULES],
        "next_action": {k: {"action": a, "note": n} for k, (a, n) in NEXT_ACTION.items()},
        "positive": sorted(POSITIVE),
    }


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(data['rules'])} rules")
