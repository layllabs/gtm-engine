# Glossary

Terms as this repo uses them. Where the industry uses the word differently,
the difference is noted so an agent does not misparse.

| term | meaning here |
|---|---|
| **signal** | An event that happened to a business: permit issued, filing registered, ownership changed, review spike, hiring post, owner's public post about fees. Not a firmographic attribute. A business existing is `listing_only`, which is kept but scored low. See `docs/signals.md`. |
| **account** | One business after dedupe, carrying every signal found for it across sources. Identified by `acc_` + sha1 of normalized name and city. |
| **lane** | Which motion an account belongs to: `direct` (sell to the merchant) or `partner` (sign a business that refers merchants). Each lane has its own ICP and sequence. |
| **ICP** | Ideal customer profile, as a JSON file in `config/icp/`: included and excluded categories, per-category fit, territory, scoring weights, signal strengths, tier thresholds. One file per lane or vertical. |
| **tier** | A, B, C, D or DQ, from the weighted score and the ICP's thresholds. DQ means excluded category, no ICP match, or out of territory; it is set before scoring, not by a low score. |
| **reasons** | Plain-English list on every scored account saying why it scored as it did. Required by schema. |
| **routing rule** | A row in `config/routing.json`: conditions on lane, tier, has_email, has_phone, has_address, suppressed; first match wins; produces an action, an optional sequence and an optional task. |
| **action** | What the rep or sequencer does next: `sequence`, `sequence_and_call`, `visit_and_sequence`, `call_first`, `nurture`, `suppress`, `disqualify`. |
| **suppression** | Emails, domains and phones that must never be contacted: unsubscribes, existing customers, do-not-contact requests, hard bounces. Checked before routing. Terminal. |
| **sequence** | A multi-step cadence of emails and calls in `config/sequences/`, with openers keyed by signal type and A/B variants on day 0. |
| **opener** | The first line of the day-0 email, chosen from the account's strongest signal. In production, rewritten by Claude and QA-reviewed; the template is the fallback. |
| **lint gate** | Checks every rendered email must pass before enrollment: no em or en dashes, no unfilled variables, word and link and question limits, no spam phrases, subject length. Failure blocks the account. |
| **variant** | A or B version of the day-0 email. Assigned by hashing the account id, so stable across reruns. Judged on positive reply rate with a z-test. |
| **positive reply** | `interested`, `question` or `meeting_request`. The metric sequences are judged on. Total replies include unsubscribes and are not used. |
| **lifecycle state** | Where an account is: new, scored, queued, task_pending, sequenced, paused, engaged, rerouted, meeting, opportunity, won, lost, nurture, closed_no, suppressed, disqualified. Transitions are validated; see `docs/crm/lifecycle.md`. |
| **event log** | Append-only list of every state change with timestamp and reason. The answer to "how did this account get here". |
| **shadow CRM** | The local SQLite database holding what the system-of-record CRM cannot flexibly hold (signals, score components, drafts, lint results, event log). Syncs a few fields to the real CRM. See ADR 002. |
| **system of record** | The company CRM (Salesforce, HubSpot, or similar). Owns accounts, contacts, opportunities and pipeline reporting. |
| **nurture** | Stopped sequence, waiting for a new signal. Not a drip campaign. A new signal sends the account back to `scored`. |
| **recycle** | A closed, lost or nurtured account re-entering at `scored` because a new signal arrived. Nothing re-enters a sequence without being rescored. |
| **deliverability** | Whether sent mail lands in the inbox. Managed here by warmup floors, bounce and complaint thresholds, send caps, placement tests and domain retirement. |
| **lookalike domain** | A sending domain similar to the brand domain, used so cold email never risks the primary domain's reputation. |
| **warmup** | Period during which a new mailbox sends and receives low-volume mail to build reputation before any cold sends. Floor here: 14 days and 95% reputation. |
| **placement test** | Sending to a seeded set of inboxes across providers to measure inbox vs spam folder rate. Weekly per domain. |
| **retire** | Take a sending domain out of rotation permanently after two of its mailboxes are paused in 30 days. |
| **rules-first** | Deterministic regex handles the obvious replies; the model only sees low-confidence cases, against a JSON schema, with a non-model fallback. |
| **eval set** | Labeled replies in `data/sample/reply_eval.jsonl`. The rules are scored against it in CI; the model prompt has to beat the rules on the same set. |
| **ADR** | Architecture decision record: a short note on a choice, its reasoning, and the condition that would reverse it. `docs/decisions/`. |
| **stated / verifiable** | Labels on the portfolio pages. Verifiable: check the file or run the command. Stated: the candidate's word, probe in interview. |
| **connector** | One entry in `gtm/integrations/registry.py`: how a tool authenticates, which env var holds the credential, a read-only probe endpoint, rate limit. |
| **AEO** | Answer engine optimization: structuring content so an AI assistant can extract and cite it. See `docs/aeo/`. |

## Payments terms

**Interchange.** The fee the card-issuing bank takes, set by the networks by card type and presentation. Pass-through; the same at any processor.

**Assessments.** The card network's own fee. Pass-through.

**Processor markup.** Everything above interchange and assessments: percentage, per-item, monthly, PCI, equipment. The only negotiable layer.

**Effective rate.** Total fees divided by volume, all-in. The first number read back in a statement review.

**Basis point (bps).** One hundredth of a percent. Markup is quoted in bps over interchange.

**Interchange-plus.** Pricing that shows interchange and markup separately. The only model the calculator will estimate savings on.

**Tiered pricing.** Qualified / mid / non-qualified blended rates that hide the markup. The calculator flags and declines.

**ETF.** Early termination fee. Payback in months is the ETF divided by the monthly difference.

**PSP.** Payment service provider: the party that processes the merchant's transactions.

**Payment orchestration.** A layer that routes transactions across more than one PSP by rules: first attempt, retry, failover, local methods.

**Authorization rate.** Approved transactions over attempted. The enterprise unit of value.

**Soft decline.** A decline the issuer may approve on retry or via another route; the first discovery question in the enterprise lane.

**Routing diagram.** The enterprise lane's first ask: a one-page map of where a merchant's transactions would go, built from their provider and country list.
