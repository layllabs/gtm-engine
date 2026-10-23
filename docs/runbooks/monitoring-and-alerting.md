# Runbook: monitoring, error handling, alerting

What can break, how I find out, and what happens automatically versus by
hand. The engine fails loudly and early: a bad input stops the run rather
than scoring garbage.

## Alert table

| Condition | Detected by | Severity | Automatic action | Human action |
|---|---|---|---|---|
| A source emits zero rows | discovery step, per-source count vs last run | warn | run continues; scoreboard shows the source at 0 | check the source's layout or auth |
| Row missing name / type / source | `discover.load_signals` | stop | run aborts with row number | fix the source adapter |
| ICP config fails schema | `scripts/validate_config.py` in CI | stop | merge blocked | fix the JSON |
| Template fails lint | `python -m gtm lint-copy` in CI | stop | merge blocked | fix the copy |
| Draft fails lint at render time | pipeline step 5 | warn | account not enrolled, listed under "blocked" | fix opener or template |
| Mailbox bounce rate over 2% | `health.check_mailboxes` | high | mailbox pulled from rotation today | verify the list it sent to; re-verify domain |
| Complaint rate over 0.1% | same | high | mailbox pulled from rotation | review copy and list source for that send |
| Two mailboxes paused on one domain in 30 days | same | high | domain marked retire | register replacement, start the domain runbook |
| Placement test under 80% inbox | weekly placement test | high | none yet | pause domain, investigate DNS and content |
| Classifier confidence under 0.7 | `replies.process` | info | reply sent to model, then review queue | review the queue daily |
| Model output fails schema | schema validation | warn | discarded, reply goes to human review | none unless frequent; then fix the prompt |
| Model API unavailable | HTTP error | warn | rules-only classification, flag for review | none; engine still runs |
| Connector credential rejected | `python -m gtm connect` | high | that integration skipped this run | rotate or re-scope the key |
| Inbound SLA breached | `inbound.sla_status` | high | escalate to owner's manager | respond, then check why routing was slow |
| Illegal lifecycle transition | `lifecycle.Ledger.move` raises | stop | run aborts | the bug is in routing or reply handling; fix before rerun |
| Nightly CI run fails | GitHub Actions | warn | badge goes red | read the failing step |

## Where alerts go

- Stop-severity: the run exits non-zero. In CI that is a red check; in the
  daily session it is the first line of the scoreboard.
- High: the scoreboard's deliverability and tasks sections, plus a chat
  message in production (the n8n export has the Slack node).
- Warn and info: scoreboard only.

## Error handling principles

1. **Fail the run, not the account.** Bad config or bad input stops
   everything before anything is scored or sent. A single account that
   cannot be enriched routes by what it has.
2. **Every model call has a non-model path.** The engine's output on a day
   the API is down is the same shape, with more items in the review queue.
3. **Nothing retries a send.** A failed enrollment is logged and listed;
   the next run picks it up. Retrying sends is how duplicates happen.
4. **State changes are validated.** The lifecycle machine refuses illegal
   moves, so a bug surfaces as an exception, not as an account quietly
   marked `won`.
5. **Everything is idempotent per day.** Rerunning the same day produces
   the same scoreboard; A/B assignment and territory are hash-based.

## Weekly review checklist

- Source row counts, week over week.
- Enrichment coverage table: any provider under 20% hit rate for two weeks
  gets demoted in `config/enrichment.json`.
- Review queue size: growing means the rules need a new pattern or the
  threshold is wrong.
- Variant z-test verdicts.
- Open SLA breaches and why.
