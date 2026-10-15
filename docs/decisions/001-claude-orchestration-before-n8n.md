# ADR 001: Run orchestration from Claude before adopting n8n

**Status:** accepted
**Date:** 2026-08

## Context

The engine needs something to sequence the steps: pull stats, classify
replies, create tasks, enroll batches. The obvious answer is n8n or a
similar workflow tool. But at this stage there are two or three workflows,
they run once a day, and every step is still changing weekly.

## Decision

Orchestrate from a Claude session following a written runbook
(`docs/workflows/`), with the deterministic parts as Python in this repo.
Defer n8n until there is something that needs to run while nobody is
watching, for example an instant response to a website form.

## Consequences

- Every step is visible and editable in plain text. Changing a workflow is
  editing a markdown file, not re-wiring nodes.
- No monthly fee while the shape of the engine is still moving.
- The engine does not run at 3am. For a daily batch that is fine. For
  event-driven work it is not, which is the trigger to revisit.
- The runbook has to be written well enough that the steps are
  reproducible. That discipline turned out to be useful on its own.

## Revisit when

An inbound lead needs a reply in minutes, or the daily run takes more
than 20 minutes of attention.
