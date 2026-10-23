# Cold AI screen, 2026-10-15

Before publishing, I had an AI reviewer with no context read the repo the way
a hiring team's screening agent would, and asked it to be harsh. This is its
report, lightly trimmed, followed by what I changed in response. I'm
publishing it because the fixes only make sense next to the criticism, and
because a portfolio that hides its review is asking you to trust it.

## The report (verbatim where it matters)

**Score: 6/10. Advance to a screen.** "The systems design, deliverability
thresholds, and copy are above the bar for a GTM Engineer, but the
interviewer must pressure-test whether any of this ever touched a live
prospect, because the repo itself cannot prove it did."

**Green flags it called out**

- Mermaid lifecycle diagram parsed by a test and diffed against the code.
  "Rare and genuinely useful."
- Scores carry plain-English reasons; suppression is checked first and terminal.
- Stable hash-based A/B assignment; template lint runs against worst-case
  long names in CI.
- Decision records with "revisit when" triggers. "Shows judgment about
  tooling, not just enthusiasm."
- Reply precedence rules are thoughtful (OOO beats "not interested in spam
  filters").

**Red flags it raised**

1. "The hard part is missing." No scrapers, no verifier, no sequencer, no
   LLM client. "A scoring-and-routing demo wearing a signal-based engine title."
2. No production evidence. Single commit, synthetic data.
3. Unbacked claims: "cheaper models were tested" with no eval.
4. Classifier bugs a senior would catch in minutes: "Reach out to me in
   March" labeled wrong_person; "Please do not send me your statement
   review again" labeled interested at 0.9.
5. `category_fit` was always 1.0 but carried 25 points. Dead weight.
6. Doc/code drift: a docstring referenced a test file that did not exist.
7. Nightly workflow "is theater": re-committed static output.
8. Thin tests: nothing for variants, OOO dates, spam lint, dedupe
   false-merge, partner routing.
9. Reddit/Craigslist scraping listed as a source with no ToS discussion.

## What I changed the same day

| Flag | Change | Where |
|---|---|---|
| 4 | Reordered rules so negatives outrank positives; tightened the `wrong_person` and `interested` patterns | `gtm/replies.py` |
| 3, 4 | Added a 28-case labeled eval set with the traps the reviewer found; `python -m gtm eval-replies` runs in CI and fails under 90% | `data/sample/reply_eval.jsonl`, `gtm/__main__.py`, `.github/workflows/ci.yml` |
| 5 | Per-category fit weights in each ICP file (restaurant 1.0, retail 0.7); retuned tier thresholds | `config/icp/*.json`, `gtm/score.py`, `schemas/icp.schema.json` |
| 6 | Fixed the docstring | `gtm/lifecycle.py` |
| 7 | Nightly job now runs with today's date so recency decays; its comment says plainly it is a smoke test on sample data | `.github/workflows/nightly-run.yml` |
| 8 | 18 tests to 26: variant z-test both ways, OOO date extraction, spam lint, same-name-different-city, partner-without-email routing | `tests/test_engine.py` |
| 3 | Removed the "cheaper models were tested" line; replaced with the actual reasoning | `prompts/reply-classifier.md` |
| 9 | Added a sourcing rule: read only, never quote, never create accounts, drop sources whose terms prohibit automated reads | `docs/workflows/01-signal-discovery.md` |
| 1 | Not fixable without publishing employer integrations. README now says this directly | `README.md`, honest notes |
| 2 | Not fixable in the repo. Every commit since this review is the history | `git log` |

## What I did not change

- The integrations stay private. The schemas are public and are the same
  ones production uses. If you want to see how a specific one is wired,
  ask and I will walk through it.
- Sample data stays synthetic. Real campaign numbers belong in a
  conversation, not a public page.

## Why this file exists

An AI screener will find most of these problems on its own. It is better
that it finds them already labeled, with the fix next to each one.
