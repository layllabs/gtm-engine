# AI guardrails

Where a model touches this system, what stops it from doing damage, and
how its quality is measured. Three model steps exist; each follows the same
five rules.

## The steps

| Step | Prompt | Output schema | Deterministic fallback | Human review |
|---|---|---|---|---|
| Opener rewrite | `prompts/opener-writer.md` | one line, QA'd by `opener-qa.md` | template opener from the sequence config | every email is approved before send |
| Reply classification | `prompts/reply-classifier.md` | `schemas/reply.schema.json` | regex rules, 28-case eval | low-confidence and all positive replies |
| Call insights | `prompts/call-insights.md` | `schemas/call_insights.schema.json` | duration, trackers, next-step phrase | rubric visible to rep; coaching digest to manager |

## The rules

1. **Rules first, model second.** Deterministic logic handles what it can
   and sets the baseline the model has to beat. `python -m gtm eval-replies`.
2. **Schema or nothing.** Model output that fails validation is discarded,
   not patched. The fallback writes instead.
3. **A separate reviewer call for anything generated.** The writer does
   not grade its own work (`opener-qa.md`). Fails fall back to the template.
4. **No model output reaches a prospect unapproved.** Drafts are drafts.
   The approval step is in the runbook and in the n8n export.
5. **Evidence over vibes.** Openers cannot state facts not in the signal
   evidence; the QA prompt fails them. Classifier changes run against the
   labeled set in CI.

## What the model is never asked to do

- Decide suppression. That is a list lookup.
- Change an account's lifecycle state directly. It returns a label; the
  state machine decides what that label means.
- Send anything.
- Quote an owner's public post or name the platform.
- Invent a number.

## Measuring

- Rules accuracy on the labeled set: `docs/eval_results.md`.
- Model accuracy: same set, same command, when the API is configured.
  The model must beat the rules on the ambiguous subset or it is not used.
- QA rejection rate on openers: tracked per run; a rising rate means the
  writer prompt drifted.
- Review queue size: the operational measure of how often the model is
  unsure.

## Known gaps

- The labeled set is small (28) and I labeled it. Open question in
  `docs/open-questions.md`.
- No adversarial cases yet (prompt injection in a reply body). The schema
  limits damage; it does not detect intent.
