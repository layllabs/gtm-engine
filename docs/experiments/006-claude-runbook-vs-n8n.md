# 006: Claude-native runbook vs n8n for daily orchestration

status: done, decision taken
dates: 2026-08
context: orchestrating the daily engine run (pull stats, classify replies,
create tasks, enroll batches) for a one-person outbound motion

## Hypothesis

A written runbook executed by Claude in a daily session would be cheaper,
more visible and easier to change than n8n workflows, as long as nothing
needed to run while nobody was watching.

## Setup

- Option A: n8n (self-hosted VPS or the hosted starter plan), each
  workflow as nodes.
- Option B: the four workflows written as markdown runbooks
  (`docs/workflows/`), with the deterministic steps as Python in this repo,
  run by Claude once a day with me present.
- Judged on: time to change a step, visibility of what ran, monthly cost,
  and whether any step actually required unattended execution.

## Result

Qualitative, not a metric test. Over the evaluation period:

- Every workflow changed at least weekly. Editing a markdown step took
  minutes; the equivalent in n8n meant re-wiring nodes and re-testing.
- No step needed to run at 3am. The daily batch was fine as a daily
  session.
- Cost: zero for the runbook route versus the n8n plan or a VPS.
- Visibility: every step and its output was in the session transcript.

Decision: runbook now, n8n deferred. Recorded as
`docs/decisions/001-claude-orchestration-before-n8n.md` with the reversal
condition.

## What I'd do differently

Write the runbooks to a stricter template from the start (trigger, inputs,
steps, outputs, failure handling). The early versions were prose and had
to be rewritten to be reproducible, which is the whole point.

## What would reverse it

An inbound lead that needs a reply in minutes, or a daily run that takes
more than 20 minutes of attention. Either one and the event-driven parts
move to n8n; the decision logic stays in this repo.

## Evidence

- `docs/decisions/001-claude-orchestration-before-n8n.md`
- `docs/workflows/01` through `05`
- `gtm/pipeline.py` (the deterministic steps the runbook calls)
