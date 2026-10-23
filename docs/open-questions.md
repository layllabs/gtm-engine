# Open questions

Things I have not solved. Listed because a portfolio that only shows
answers is hiding the interesting part, and because an interviewer who
asks about one of these should get a real conversation, not a bluff.

## Catch-all domains

A verifier returns "catch-all" for a domain that accepts every address.
The engine routes those to call-first instead of enrolling. That is safe
and slow. Options I have not tested: send one low-stakes touch to catch-all
addresses from a sacrificial mailbox and promote the ones that do not
bounce; or score catch-all by domain age and MX provider. Both add
complexity for a minority of accounts.

## Consent and public posts

Owner posts on public forums are the strongest intent signal and the
most ethically loaded. Current rule: read for topic only, never quote,
never name the platform, drop any source whose terms prohibit automated
reads. Open: whether "read for topic" is a distinction the owner would
accept if they knew. I think yes for a post that is literally asking for
help with fees. I am less sure for a hiring post.

## When to leave SQLite

The shadow CRM is one file. Fine for one rep, wrong for two. The schema
does not change on Postgres, but the sync-to-CRM step does. Trigger I am
using: the day a second person needs to read it while I am writing to it.

## Scoring weights are a hypothesis

Weights in `config/icp/*.json` are what I believe, not what I have
measured. The test is positive reply rate by tier over 30+ outcomes per
tier. Until then, the honest description is "ranked by my judgment,
expressed as numbers so I can be wrong in a specific way."

## The model boundary

Rules handle the obvious replies. Claude handles the rest. Where exactly
the line sits is set by one confidence threshold (0.7). I have not swept
it. Lower means more model calls and fewer misses; higher means cheaper
and more unknowns to review by hand. The right value depends on reply
volume and how expensive a missed meeting is, which varies by lane.

## Walk-ins do not fit the event log cleanly

A visit is a task with a due date, but what happened on the visit (owner
not there, left a card, got the statement) is richer than a state
transition. Right now it lands in the task note. Probably needs its own
small table.

## Signals I want and cannot get yet

POS hardware for sale by the owner, lease signings, imagery-derived size
markers. See the bottom of `docs/signals.md`.

## What I would ask someone who has done this longer

1. How do you keep an eval set honest when you are the one labeling it?
2. At what send volume did a dedicated sender beat sequencer-native sending for you, and what broke first?
3. Is there a signal source for local merchants I am missing that is both legal and not already saturated?
