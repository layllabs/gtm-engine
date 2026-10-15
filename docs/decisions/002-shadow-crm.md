# ADR 002: Keep a local shadow CRM next to the system of record

**Status:** accepted
**Date:** 2026-08

## Context

The engine produces data the CRM has no fields for: five score
components per account, which signal fired and when, which copy variant
went out, lint results, reply labels with confidence, a full state log.
Getting custom fields added means a RevOps ticket per field, and most of
these fields will change as the model is tuned.

## Decision

SQLite file, schema in `gtm/store.py`, rebuilt on every run from the
engine's outputs. The CRM gets a small set of synced fields that a
manager or another rep would actually look at (see
`docs/crm/data-model.md`).

## Consequences

- Any question about the engine is a SQL query, not a report request.
- Tuning the scoring model does not touch the CRM at all.
- Two places to look. Mitigated by syncing only what others need and
  keeping the CRM as the single source of truth for pipeline.
- SQLite is single-user. If a second rep joins, this becomes Postgres.
  The schema does not change.
