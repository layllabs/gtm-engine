# 001: Signal-based openers vs generic openers

status: running
dates: 2026-09 to present
context: direct lane, owner-operated local merchants, synthetic numbers in
this repo; real numbers discussed in conversation

## Hypothesis

An opening line that references the specific event that put the account in
the queue (a permit, a filing, an ownership change, an owner's public post
about fees) will produce a higher positive-reply rate than a generic opener
about the category and city, because it proves the email is not a blast.

## Setup

- Control: `listing_only` opener ("I work with a lot of {category} owners
  around {city}").
- Treatment: opener chosen from the account's strongest signal
  (`config/sequences/local-merchant-v2.json`, `openers` block).
- Same body, same ask, same send windows, same mailboxes.
- Variant assignment is stable per account (hash of account id), so a rerun
  never flips an account between arms.
- Success metric: positive reply rate (interested, question,
  meeting_request), not total replies. An unsubscribe is a reply.
- Decision rule: two-proportion z-test, |z| >= 1.96 before promoting.
  `gtm/health.py::check_variants`.

## Result

Synthetic sample in this repo: variant A 0.95% positive on 420 sends vs B
0.25% on 405, z = 1.31, not significant. The engine's own verdict: "keep
testing." Real results are not published here.

## What I'd do differently

Run the opener test separately from the body test. v2 changed both the
opener and the ask at the same time, which means the lift cannot be
attributed cleanly. The next sequence version changes one thing.

## Evidence

- `config/sequences/local-merchant-v2.json`
- `docs/copy/local-merchant-v2.md` (line-by-line rationale, v1 to v2 diff)
- `gtm/copywriting.py::assign_variant`, `gtm/health.py::check_variants`
- `tests/test_engine.py::test_variant_verdict_not_significant_on_small_sample`
