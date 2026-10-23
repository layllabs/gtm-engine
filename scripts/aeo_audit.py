"""Audit an HTML page for the SEO/AEO checklist in docs/aeo/README.md.

    python scripts/aeo_audit.py docs/index.html docs/human.html

Exit 1 if any required check fails. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def checks(html: str, path: Path) -> list[tuple[str, bool, str, bool]]:
    """Returns (name, passed, detail, required)."""
    out = []
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    t = title.group(1).strip() if title else ""
    out.append(("title present, under 60 chars", 0 < len(t) <= 60, f"{len(t)} chars", True))
    desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    d = desc.group(1) if desc else ""
    out.append(("meta description 50 to 160 chars", 50 <= len(d) <= 160, f"{len(d)} chars", True))
    out.append(("canonical link", 'rel="canonical"' in html, "", True))
    out.append(("Open Graph title and description", 'property="og:title"' in html and 'property="og:description"' in html, "", True))
    out.append(("viewport meta", 'name="viewport"' in html, "", True))
    out.append(("lang attribute", re.search(r"<html[^>]+lang=", html) is not None, "", True))

    ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    types = []
    valid = True
    for b in ld_blocks:
        try:
            data = json.loads(b)
            types.append(data.get("@type"))
        except ValueError:
            valid = False
    out.append(("JSON-LD parses", valid and bool(ld_blocks), f"types {types}", True))
    out.append(("Person schema", "Person" in types, "", True))
    out.append(("FAQPage schema", "FAQPage" in types, "", path.name == "index.html"))

    out.append(("links to llms.txt", "llms.txt" in html, "", True))
    out.append(("links to portfolio.json", "portfolio.json" in html, "", True))
    out.append(("last updated date", re.search(r"(Last updated|last_updated)[^0-9]*20\d\d-\d\d-\d\d", html) is not None, "", True))
    out.append(("no em or en dashes", "\u2014" not in html and "\u2013" not in html, "", True))
    heads = re.findall(r"<h2[^>]*id=\"([^\"]+)\"", html)
    out.append(("section ids on h2 headings", len(heads) >= 5, f"{len(heads)} ids", path.name == "index.html"))
    words = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", html)))
    out.append(("content without JS (word count)", words > 400, f"{words} words", True))
    return out


def main(paths: list[str]) -> int:
    failed = 0
    for p in paths:
        path = Path(p)
        html = path.read_text(encoding="utf-8")
        print(f"\n{path}")
        for name, ok, detail, required in checks(html, path):
            mark = "PASS" if ok else ("FAIL" if required else "warn")
            if not ok and required:
                failed += 1
            print(f"  {mark} {name} {detail}")
    print(f"\n{failed} required checks failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["docs/index.html", "docs/human.html"]))
