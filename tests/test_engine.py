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


class TestEndToEnd(unittest.TestCase):
    def test_run(self):
        out = Path(ROOT / "examples" / "_test_output")
        res = run(DATA, out, AS_OF)
        self.assertTrue((out / "scoreboard.md").exists())
        self.assertTrue((out / "engine.db").exists())
        self.assertFalse(any(d["lint"] for d in res["drafts"]))


if __name__ == "__main__":
    unittest.main()
