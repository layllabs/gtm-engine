import json
import re
import unittest
from datetime import date
from pathlib import Path

from gtm import copywriting, dedupe, discover, health, replies, route, score
from gtm.lifecycle import TRANSITIONS, InvalidTransition, Ledger
from gtm.pipeline import run
from gtm.util import ROOT, norm_name

DATA = ROOT / "data" / "sample"
AS_OF = date(2026, 10, 1)


class TestDedupe(unittest.TestCase):
    def test_name_normalization(self):
        self.assertEqual(norm_name("Rosa's Taqueria LLC"), norm_name("Rosas Taqueria"))
        self.assertEqual(norm_name("Harbor Brake & Tire"), norm_name("Harbor Brake and Tire"))

    def test_same_name_different_city_does_not_merge(self):
        rows = [
            {"source": "maps", "source_id": "1", "business_name": "Main Street Cafe", "category": "cafe", "address": "",
             "city": "Ventura", "state": "CA", "zip": "", "phone": "", "website": "", "email": "", "contact_name": "",
             "signal_type": "listing_only", "signal_date": None, "signal_text": "", "review_count": None, "rating": ""},
            {"source": "maps", "source_id": "2", "business_name": "Main Street Cafe", "category": "cafe", "address": "",
             "city": "Oxnard", "state": "CA", "zip": "", "phone": "", "website": "", "email": "", "contact_name": "",
             "signal_type": "listing_only", "signal_date": None, "signal_text": "", "review_count": None, "rating": ""},
        ]
        self.assertEqual(len(dedupe.merge(rows)), 2)

    def test_merges_across_sources(self):
        accts = dedupe.merge(discover.load_signals(DATA / "raw_signals.csv"))
        rosa = next(a for a in accts if "Rosa" in a["business_name"])
        self.assertEqual(set(rosa["sources"]), {"maps", "county_permits"})
        harbor = next(a for a in accts if "Harbor" in a["business_name"])
        self.assertIn("reddit", harbor["sources"])  # joined by name+city, no phone on the post


class TestScoring(unittest.TestCase):
    def setUp(self):
        accts = dedupe.merge(discover.load_signals(DATA / "raw_signals.csv"))
        self.scored = {a["business_name"]: a for a in score.score_all(accts, score.load_icps(), AS_OF)}

    def test_exclusions(self):
        self.assertEqual(self.scored["First Coastal Bank"]["tier"], "DQ")
        self.assertEqual(self.scored["SwiftPay Merchant Services"]["tier"], "DQ")
        self.assertIn("out of territory", self.scored["Neon Taco Co"]["reasons"][0])

    def test_fresh_signal_beats_listing(self):
        self.assertGreater(self.scored["Harbor Brake and Tire"]["score"], self.scored["Mesa Verde Market"]["score"])

    def test_every_scored_account_explains_itself(self):
        for a in self.scored.values():
            self.assertTrue(a["reasons"], a["business_name"])


class TestRouting(unittest.TestCase):
    def test_suppression_wins(self):
        accts = dedupe.merge(discover.load_signals(DATA / "raw_signals.csv"))
        routed = route.route_all(score.score_all(accts, score.load_icps(), AS_OF),
                                 route.load_suppression(DATA / "suppression.csv"), AS_OF)
        by = {a["business_name"]: a for a in routed}
        self.assertEqual(by["Pier Avenue Books"]["action"], "suppress")
        self.assertEqual(by["Paws & Claws Vet Clinic"]["action"], "suppress")

    def test_partner_without_email_goes_to_call_first(self):
        accts = dedupe.merge(discover.load_signals(DATA / "raw_signals.csv"))
        routed = route.route_all(score.score_all(accts, score.load_icps(), AS_OF),
                                 route.load_suppression(DATA / "suppression.csv"), AS_OF)
        inland = next(a for a in routed if a["business_name"] == "Inland Kitchen Repair")
        self.assertEqual(inland["lane"], "partner")
        self.assertEqual(inland["action"], "call_first")

    def test_no_email_never_enrolls(self):
        accts = dedupe.merge(discover.load_signals(DATA / "raw_signals.csv"))
        routed = route.route_all(score.score_all(accts, score.load_icps(), AS_OF),
                                 route.load_suppression(DATA / "suppression.csv"), AS_OF)
        for a in routed:
            if a["sequence"]:
                self.assertTrue(a["email"], a["business_name"])


class TestCopy(unittest.TestCase):
    def test_templates_pass_lint(self):
        bad = [x for x in copywriting.lint_templates(copywriting.load_sequences()) if x["issues"]]
        self.assertEqual(bad, [])

    def test_lint_catches_em_dash(self):
        issues = copywriting.lint("hi", "Great question \u2014 here's why", {"max_words": 90, "max_links": 0, "max_questions": 1})
        self.assertTrue(any("dash" in i for i in issues))

    def test_lint_catches_unfilled_var(self):
        issues = copywriting.lint("hi", "Hi {{first_name}}", {"max_words": 90, "max_links": 0, "max_questions": 1})
        self.assertTrue(any("unfilled" in i for i in issues))

    def test_lint_catches_spam_phrase(self):
        issues = copywriting.lint("hi", "Act now for a risk-free review", {"max_words": 90, "max_links": 0, "max_questions": 1})
        self.assertTrue(any("spam" in i for i in issues))

    def test_variant_is_stable(self):
        seq = copywriting.load_sequences()["local-merchant-v2"]
        self.assertEqual(copywriting.assign_variant("acc_x", seq), copywriting.assign_variant("acc_x", seq))


class TestReplies(unittest.TestCase):
    def test_labels(self):
        cases = {
            "Please remove me from your list.": "unsubscribe",
            "I'm out of the office until October 8.": "out_of_office",
            "We're locked in a contract until March. Reach out then.": "not_now",
            "Can you do Thursday at 2?": "meeting_request",
            "Not interested, we already have a guy.": "not_interested",
        }
        for body, label in cases.items():
            self.assertEqual(replies.classify(body)[0], label, body)

    def test_negatives_beat_positive_keywords(self):
        self.assertEqual(replies.classify("Please do not send me your statement review again")[0], "not_interested")
        self.assertEqual(replies.classify("Reach out to me in March")[0], "not_now")

    def test_labeled_eval_set(self):
        from gtm.util import read_jsonl
        rows = read_jsonl(DATA / "reply_eval.jsonl")
        correct = sum(1 for r in rows if replies.classify(r["body"])[0] == r["label"])
        self.assertGreaterEqual(correct / len(rows), 0.9)

    def test_ooo_resume_date(self):
        info = replies.extract("out_of_office", "out of the office until October 8", AS_OF)
        self.assertEqual(info["resume_on"], "2026-10-09")

    def test_follow_up_date(self):
        info = replies.extract("not_now", "contract until March", AS_OF)
        self.assertEqual(info["follow_up_on"], "2027-03-01")


class TestHealth(unittest.TestCase):
    def test_domain_retired_when_two_boxes_paused(self):
        import json
        stats = json.loads((DATA / "mailbox_stats.json").read_text())
        _, domains = health.check_mailboxes(stats)
        verdicts = {d["domain"]: d["verdict"] for d in domains}
        self.assertEqual(verdicts["sender-two.example"], "retire and replace")


    def test_variant_verdict_not_significant_on_small_sample(self):
        stats = {"mailboxes": [], "variants": [
            {"sequence": "s", "variant": "A", "sent": 420, "replies": 9, "positive": 4},
            {"sequence": "s", "variant": "B", "sent": 405, "replies": 5, "positive": 1}]}
        rows = health.check_variants(stats)
        self.assertIn("not significant", rows[0]["verdict"])

    def test_variant_verdict_significant_on_large_sample(self):
        stats = {"mailboxes": [], "variants": [
            {"sequence": "s", "variant": "A", "sent": 4000, "replies": 90, "positive": 60},
            {"sequence": "s", "variant": "B", "sent": 4000, "replies": 50, "positive": 20}]}
        rows = health.check_variants(stats)
        self.assertIn("promote", rows[0]["verdict"])


class TestLifecycle(unittest.TestCase):
    def test_illegal_jump_rejected(self):
        led = Ledger()
        with self.assertRaises(InvalidTransition):
            led.move("a", "won", "skip everything", "t")

    def test_suppressed_is_terminal(self):
        self.assertEqual(TRANSITIONS["suppressed"], set())

    def test_mermaid_diagram_matches_code(self):
        doc = (ROOT / "docs" / "crm" / "lifecycle.md").read_text()
        edges = set(re.findall(r"^\s*(\w+)\s*-->\s*(\w+)", doc, re.M))
        edges = {(a, b) for a, b in edges if a != "start"}
        code = {(a, b) for a, bs in TRANSITIONS.items() for b in bs}
        self.assertEqual(edges, code)


class TestPlaygroundSync(unittest.TestCase):
    def test_rules_json_matches_python(self):
        import json, sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from export_rules import build
        on_disk = json.loads((ROOT / "docs" / "rules.json").read_text())
        self.assertEqual(on_disk, build(), "run: python scripts/export_rules.py")


class TestEnrichment(unittest.TestCase):
    def _acct(self, **kw):
        base = {"account_id": "acc_t1", "business_name": "Test Cafe", "category": "cafe", "contact_name": "Ana Ruiz",
                "email": "", "phone": "", "website": "", "review_count": None, "sources": ["maps"], "signals": []}
        base.update(kw); return base

    def test_crm_is_free_and_first(self):
        from gtm import enrich
        _, log = enrich.enrich(self._acct(email="", sources=["partner_scan"]))
        self.assertEqual(log[0]["provider"], "crm"); self.assertEqual(log[0]["cost_cents"], 0)

    def test_pattern_guess_never_enrolls(self):
        from gtm import enrich
        cfg = json.loads((ROOT / "config" / "enrichment.json").read_text())
        cfg["fields"]["email"]["providers"] = ["pattern_guess"]
        out, _ = enrich.enrich(self._acct(website="testcafe.example"), cfg)
        self.assertTrue(out["email"].endswith("@testcafe.example"))
        self.assertTrue(out["needs_verification"])
        routed = route.route_all([{**out, "icp": "local-merchant", "lane": "direct", "tier": "A", "score": 90,
                                   "address": "1 Main", "state": "CA", "components": {}, "reasons": ["x"]}],
                                 {"email": set(), "domain": set(), "phone": set()}, AS_OF)
        self.assertIsNone(routed[0]["sequence"])
        self.assertEqual(routed[0]["action"], "call_first")

    def test_budget_skips_expensive_provider(self):
        from gtm import enrich
        cfg = json.loads((ROOT / "config" / "enrichment.json").read_text())
        cfg["fields"]["email"]["max_cost_cents"] = 1
        _, log = enrich.enrich(self._acct(), cfg)
        self.assertTrue(any(e["provider"] == "apollo" and e["result"] == "skipped_budget" for e in log))


class TestTerritory(unittest.TestCase):
    def test_zip_beats_state_and_partner_override_wins(self):
        from gtm import territory
        self.assertEqual(territory.assign({"account_id": "a", "lane": "direct", "zip": "93401", "state": "CA"})[0], "rep_cc")
        self.assertEqual(territory.assign({"account_id": "a", "lane": "direct", "zip": "", "state": "CA"})[0], "rep_ca_overflow")
        self.assertEqual(territory.assign({"account_id": "a", "lane": "partner", "zip": "93401", "state": "CA"})[0], "rep_partners")

    def test_round_robin_is_stable(self):
        from gtm import territory
        a = {"account_id": "acc_rr", "lane": "direct", "zip": "90012", "state": "CA"}
        self.assertEqual(territory.assign(a)[0], territory.assign(a)[0])
        self.assertIn(territory.assign(a)[0], ("rep_la1", "rep_la2"))


class TestInbound(unittest.TestCase):
    def test_hot_lead_gets_five_minute_sla_and_owner(self):
        from datetime import datetime
        from gtm import inbound
        acct = inbound.intake({"business_name": "Quick Lube", "contact_name": "Sam Lee", "email": "sam@ql.example",
                               "zip": "93401", "state": "CA", "category": "auto_repair",
                               "message": "Our contract ends next month, can you send pricing?",
                               "utm_source": "google", "utm_medium": "cpc", "utm_campaign": "fees"},
                              datetime(2026, 10, 1, 9, 0))
        self.assertEqual(acct["intent"], "hot"); self.assertEqual(acct["sla_minutes"], 5)
        self.assertEqual(acct["owner"], "rep_cc")
        self.assertEqual(acct["attribution"]["first_touch_source"], "google")
        self.assertIn("statement", acct["first_response"])
        self.assertEqual(inbound.sla_status(acct, datetime(2026, 10, 1, 9, 4)), "on_time")
        self.assertEqual(inbound.sla_status(acct, datetime(2026, 10, 1, 9, 6)), "breached")


class TestSqlQueries(unittest.TestCase):
    def test_every_named_query_runs(self):
        import re, sqlite3
        from gtm.pipeline import run
        out = ROOT / "examples" / "_test_output"
        run(DATA, out, AS_OF)
        text = (ROOT / "docs" / "sql" / "analysis.sql").read_text()
        blocks = re.findall(r"-- name: (\w+)\n((?:--.*\n)*)([\s\S]*?;)", text)
        self.assertGreaterEqual(len(blocks), 8)
        con = sqlite3.connect(out / "engine.db")
        for name, _, q in blocks:
            con.execute(q).fetchall()


class TestEvalExport(unittest.TestCase):
    def test_eval_results_json_matches_current_rules(self):
        import json, sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from export_eval import run
        on_disk = json.loads((ROOT / "docs" / "eval_results.json").read_text())
        self.assertEqual(on_disk, run(), "run: python scripts/export_eval.py")


class TestIntegrations(unittest.TestCase):
    def test_registry_is_consistent(self):
        from gtm.integrations import REGISTRY
        keys = [c.key for c in REGISTRY]
        self.assertEqual(len(keys), len(set(keys)))
        example = (ROOT / ".env.example").read_text()
        for c in REGISTRY:
            for var in c.env:
                self.assertIn(var + "=", example, f"{var} missing from .env.example")

    def test_report_without_probe_makes_no_network_calls(self):
        import os
        from gtm.integrations import report
        saved = {k: os.environ.pop(k) for k in list(os.environ) if k in ("GITHUB_TOKEN",)}
        try:
            rows = report(live=False)
            self.assertTrue(all(r["status"] in ("missing", "configured") for r in rows))
        finally:
            os.environ.update(saved)


class TestAeoAudit(unittest.TestCase):
    def test_portfolio_pages_pass(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from aeo_audit import checks
        for name in ("index.html", "human.html"):
            path = ROOT / "docs" / name
            failing = [c for c in checks(path.read_text(), path) if c[3] and not c[1]]
            self.assertEqual(failing, [], name)


class TestEndToEnd(unittest.TestCase):
    def test_run(self):
        out = Path(ROOT / "examples" / "_test_output")
        res = run(DATA, out, AS_OF)
        self.assertTrue((out / "scoreboard.md").exists())
        self.assertTrue((out / "engine.db").exists())
        self.assertFalse(any(d["lint"] for d in res["drafts"]))


if __name__ == "__main__":
    unittest.main()
