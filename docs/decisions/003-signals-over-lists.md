# ADR 003: Start from signals, not from lists

**Status:** accepted
**Date:** 2026-08

## Context

The standard SMB outbound motion is: export every business in a category
and territory from a data provider, sequence all of them, sort by reply.
It works at volume. It also burns domains, annoys thousands of owners who
have no reason to switch this month, and gives the rep no reason to call
one account before another.

## Decision

Discovery starts from events: a new health permit, a new state filing, an
ownership change, a review spike, an owner posting about fees. A business
enters the engine because something happened, and the thing that happened
decides the opener. Plain listings are kept but scored low.

## Consequences

- Lower volume, much higher relevance. The first line of every email is
  true and specific.
- The rep's call list is ordered by timing, not alphabet.
- More discovery work: permits and filings are scraped per county and
  state, and each source is its own small agent.
- Some good accounts never fire a signal. The partner lane and the
  nurture-to-rescored loop are the answer: when a signal eventually
  appears, the account comes back.

## Revisit when

Signal volume in a territory is too low to fill the day. Then widen the
signal list before falling back to plain lists.
