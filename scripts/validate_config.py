"""Validate every config file against its schema. Run in CI."""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("pip install jsonschema")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
ok = True
icp_schema = json.loads((ROOT / "schemas" / "icp.schema.json").read_text())
for p in sorted((ROOT / "config" / "icp").glob("*.json")):
    cfg = json.loads(p.read_text())
    try:
        jsonschema.validate(cfg, icp_schema)
        total = sum(cfg["weights"].values())
        if total != 100:
            raise ValueError(f"weights sum to {total}, expected 100")
        print(f"ok   {p.relative_to(ROOT)}")
    except (jsonschema.ValidationError, ValueError) as e:
        ok = False
        print(f"FAIL {p.relative_to(ROOT)}: {e}")

routing = json.loads((ROOT / "config" / "routing.json").read_text())
seq_ids = {p.stem for p in (ROOT / "config" / "sequences").glob("*.json")}
for rule in routing["rules"]:
    if rule["sequence"] and rule["sequence"] not in seq_ids:
        ok = False
        print(f"FAIL routing rule {rule['name']} references unknown sequence {rule['sequence']}")
if routing["rules"][-1]["when"] != {}:
    ok = False
    print("FAIL last routing rule must be a catch-all")
print("ok   config/routing.json" if ok else "")
sys.exit(0 if ok else 1)
