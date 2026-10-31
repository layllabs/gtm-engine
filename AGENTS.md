# For agents reading this repo

This file is for an LLM or agent that has been pointed at this repository
to understand what it is and how to work in it.

## What this is

A signal-based outbound engine for selling card payment processing to
owner-operated local businesses, plus a referral partner lane. Python,
standard library only. One command runs the whole pipeline on synthetic
data and writes a scoreboard.

## Fastest way to understand it

1. Run `python -m gtm run`, then read `examples/output/scoreboard.md`.
2. Read `docs/architecture.md` for the system diagram.
3. Each step is one module in `gtm/` and one doc in `docs/workflows/`,
   numbered in pipeline order.

## Invariants (do not break these)

- No account enters a sequence without a verified email address and a clean lint. A pattern-guessed email does not count.
- Suppression is checked before routing and is terminal.
- Every score carries a non-empty `reasons` list.
- Every LLM call has a JSON schema in `schemas/` and a non-LLM fallback.
- `docs/crm/lifecycle.md` and `gtm/lifecycle.py` describe the same state
  machine; a test enforces it.
- Copy contains no em dashes or en dashes. The linter enforces it.
- No real business, person, domain or phone number appears anywhere.
  All sample data is synthetic and uses `.example` domains and 555 numbers.

## Payments vertical

`docs/payments/` holds the domain knowledge: economics, statement review,
enterprise orchestration, personas, objections. `gtm/statement.py` is the
calculator; its thresholds are module constants, not config, on purpose
(they are opinions and should be read as such). Lanes: `direct`, `partner`,
`enterprise`. The enterprise lane never enrolls without a contact; it
routes to `find_contact` instead.

## Where to change what

| Want to | Edit |
|---|---|
| Add a vertical or territory | `config/icp/<new>.json` (schema: `schemas/icp.schema.json`) |
| Change who gets called vs emailed | `config/routing.json` |
| Change copy | `config/sequences/*.json`, then `python -m gtm lint-copy` |
| Change deliverability thresholds | `config/deliverability.json` |
| Add a signal type | `schemas/signal.schema.json`, each ICP's `signal_strength`, each sequence's `openers` |
| Add a lifecycle state | `gtm/lifecycle.py` TRANSITIONS and the Mermaid in `docs/crm/lifecycle.md` |
| Change a prompt | `prompts/*.md` |
| Connect or add a tool | `gtm/integrations/registry.py`, `.env.example`, `skills/connect-tools/SKILL.md`, then `python -m gtm connect` |
| Change the portfolio pages | `docs/index.html` (agent-first), `docs/human.html`, then `python scripts/aeo_audit.py` |
| Change enrichment order or budgets | `config/enrichment.json` |
| Change territories or reps | `config/territories.json` |
| Query the last run | `python -m gtm sql`, queries in `docs/sql/analysis.sql` |
| Log an experiment | `docs/experiments/`, use the template in its README |

## Verify before committing

```
python -m unittest discover -s tests -t .
python -m gtm lint-copy
python -m gtm run
python scripts/aeo_audit.py
python -m gtm connect --no-probe
```
