"""Small shared helpers. Standard library only so the demo runs anywhere."""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"

_SUFFIXES = re.compile(r"\b(llc|inc|co|corp|ltd|company)\b\.?", re.I)
_STORE_NO = re.compile(r"#\s*\d+")


def load_json(path: Path | str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_csv(path: Path | str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")


def read_jsonl(path: Path | str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def norm_name(name: str) -> str:
    """'Rosa's Taqueria LLC' and 'Rosas Taqueria' -> 'rosas taqueria'."""
    s = (name or "").lower().replace("&", " and ").replace("'", "")
    s = _STORE_NO.sub(" ", s)
    s = _SUFFIXES.sub(" ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_business_name(name: str) -> str:
    """Display name for copy: drops legal suffixes and store numbers."""
    s = _STORE_NO.sub("", name or "")
    s = re.sub(r",?\s+\b(LLC|Inc|Corp|Ltd)\b\.?", "", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def phone_digits(phone: str) -> str:
    d = re.sub(r"\D", "", phone or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 else ""


def domain_of(value: str) -> str:
    v = (value or "").strip().lower()
    if not v:
        return ""
    if "@" in v:
        v = v.split("@", 1)[1]
    v = re.sub(r"^https?://", "", v)
    v = v.split("/", 1)[0]
    return v[4:] if v.startswith("www.") else v


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "")[:10])
    except ValueError:
        return None


def to_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
