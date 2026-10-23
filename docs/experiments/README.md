# Experiments log

Things I tried in outbound, written up the same way every time so they can
be compared. One file per experiment. The template is below; an entry is
not published until the numbers in it are ones I can defend in an interview.

## Format

```
# <short name>
status: planned | running | done | abandoned
dates: YYYY-MM to YYYY-MM
context: anonymized (which lane, what ICP, roughly what volume)

## Hypothesis
One sentence. What I expected and why.

## Setup
What changed vs the control. Sample sizes. How success was measured.

## Result
Numbers with denominators. Or "inconclusive, N too small".

## What I'd do differently
One or two lines.

## Evidence
Links to config, copy, or data in this repo where they exist.
```

## Entries

| # | Experiment | Status |
|---|---|---|
| 001 | [Signal-based openers vs generic openers](001-signal-openers.md) | running, see docs/copy/local-merchant-v2.md for the hypothesis |
| 002 | Referral partner lane vs direct-only outbound | planned write-up |
| 003 | Public-records discovery (permits, state filings) as a lead source | planned write-up |
| 004 | Owner forum posts as an intent signal | planned write-up |
| 005 | Lookalike sending domains vs the primary domain | planned write-up |
| 006 | [Claude-native runbook vs n8n for daily orchestration](006-claude-runbook-vs-n8n.md) | done |
| 007 | Walk-in after email vs email only, for tier A local merchants | planned write-up |
| 008 | "Send me one statement" ask vs "15 minutes" ask | folded into 001 |
| 009 | AI phone answering on an inbound line for a service business | planned write-up |
| 010 | Neighborhood app (Nextdoor-style) as a local lead channel | planned write-up |

Planned entries are titles only until the write-up exists. Nothing in this
folder names an employer, client, or prospect.
