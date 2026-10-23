# Signal catalog

Every row that enters the engine carries one of these signal types. This
table is the single place that says what each one means, where it comes
from, why it predicts a conversation, and how much weight each ICP gives it.
Weights are copied from `config/icp/*.json`; if they disagree, the config
wins and this file is wrong.

| signal_type | emitted by | what happened | why now is a good time to call | direct weight | partner weight | opener exists |
|---|---|---|---|---|---|---|
| `processor_complaint` | reddit, craigslist | Owner posted publicly about card fees or their processor | The pain is stated in their own words. Highest intent we have. | 1.00 | n/a | direct |
| `new_health_permit` | county_permits | New food facility or mobile food permit issued | A new restaurant picks a processor in its first weeks, usually in a hurry | 0.90 | n/a | direct |
| `new_business_filing` | sos_filings, partner_scan | New LLC or corporation registered with the state | Same moment as the permit, one step earlier | 0.85 | 0.40 | direct, partner |
| `ownership_change` | maps | Listing shows new owner or "under new ownership" | New owners inherit the old contract without reading it | 0.85 | n/a | direct |
| `partner_program_page` | partner_scan | Business already lists vendor partners for its customers | The referral ask is familiar, not strange | n/a | 1.00 | partner |
| `review_spike` | maps, partner_scan | Unusual number of new reviews in a short window | More volume makes fees matter more every month | 0.60 | 0.50 | direct, partner |
| `hiring_post` | maps, craigslist, partner_scan | Hiring, chair rental, or growth post | Growing shops feel processing cost right about now | 0.50 | 0.60 | direct, partner |
| `listing_only` | maps, partner_scan | The business exists; nothing happened | Not an event. Kept so the account is known, scored low (recency fixed at 0.1) | 0.20 | 0.40 | direct, partner (generic line) |

## How a signal moves through the engine

1. **Discovery** (`gtm/discover.py`): a source agent writes rows in the shape
   of `schemas/signal.schema.json`. Required: `source`, `business_name`,
   `signal_type`. A row missing any of these stops the run.
2. **Dedupe** (`gtm/dedupe.py`): rows about the same business merge into one
   account that keeps every signal. Two distinct signal types on one account
   add +0.1 to signal strength ("stacked signals" shows up in reasons).
3. **Scoring** (`gtm/score.py`): the strongest signal sets `signal_strength`
   and its date sets `recency` (half-life 30 days direct, 90 partner).
4. **Copy** (`gtm/copywriting.py`): the strongest signal that has an opener
   in the sequence picks the first line. Owner posts set the topic; the post
   is never quoted and the platform is never named.
5. **Recycling** (`gtm/lifecycle.py`): a new signal on a closed or nurtured
   account sends it back to `scored`. Nothing re-enters a sequence without
   being rescored on the new event.

## Adding a signal type

1. Add it to the enum in `schemas/signal.schema.json`.
2. Give it a strength in each ICP that should see it (`config/icp/*.json`).
3. Write an opener for it in each sequence (`config/sequences/*.json`), then
   `python -m gtm lint-copy`.
4. Add a row here.
5. Add a sample row to `data/sample/raw_signals.csv` and a test if the
   routing should change.

## Signals I want and do not have yet

- POS hardware listed for sale by the owner (marketplace scrape): strong
  switch signal, no clean source yet.
- Lease signings for retail and restaurant space: public in some counties,
  not others.
- Imagery-derived markers (outdoor seating density, loading docks) as a size
  proxy where review counts are thin. Exploratory; cost per image matters.
