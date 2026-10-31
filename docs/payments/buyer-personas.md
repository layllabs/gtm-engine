# Buyer personas in payments

## SMB: the owner

One person. They opened the business, they run the register some days,
they signed the processing contract because the POS salesperson or the
bank handed it to them. What they know about processing is the monthly
fee total and that it feels high.

| | |
|---|---|
| Reads email | on a phone, between customers, before 8am or after 9pm |
| Trusts | other owners, their bookkeeper, the person who shows up in person |
| Distrusts | anyone who leads with a rate, anyone who badmouths their current vendor |
| Decides on | a number they can check themselves against their own statement |
| Delays because | contract lock, ETF, "my guy," fear of equipment changes |
| The right ask | one statement, one photo |
| The wrong ask | a 15 minute meeting, a demo, a "quick call" |

Variants:

- **New owner** (`ownership_change`): inherited the contract, has not read
  it, is already changing vendors. Highest receptiveness.
- **Just opened** (`new_health_permit`, `new_business_filing`): signed
  something in a rush, usually tiered or flat, often with a lease. Does not
  know their effective rate because they have one statement.
- **Growing** (`review_spike`, `hiring_post`): volume up, fees up, noticing
  for the first time.
- **Complained publicly** (`processor_complaint`): has done the math
  already. Wants a specific answer, not sympathy.

## SMB: the bookkeeper

Often the person who actually sees the statement. Cares about clean
reporting and not having to re-explain fees to the owner. A referral
partner, not a buyer: see the partner lane.

## Enterprise: Head of Payments

Owns cost per transaction, authorization rate, provider relationships and
reconciliation. Measured on a number they may not have good tooling to
see. Has been pitched by every PSP and is tired of provider-count slides.

- Wants: leverage over providers, a routing layer they do not have to
  build, fewer integrations to maintain, a cleaner view of auth rates by
  market and method.
- Fears: a migration that breaks checkout, vendor lock-in that replaces
  the lock-in they have, a tool their engineers will resent.
- Responds to: a diagram of their own provider mix, a pilot with a before
  and after, references in their geography.

## Enterprise: engineering leader

Owns checkout uptime and the integration backlog. Every new PSP is a
project they did not ask for.

- Wants: one integration, failover they do not have to write, less
  on-call for payments incidents.
- Fears: another vendor in the critical path, latency, a black box they
  cannot debug.
- Responds to: integration time, API docs, incident handling, what
  happens when the orchestration layer itself is down.

## Enterprise: finance

Enters at evaluation. Cares about recovered revenue from auth-rate lift,
fee consolidation, chargeback cost, and whether the vendor's pricing
scales with volume in a way that eats the gain.

## What all of them share

Nobody wants to be sold processing. Everybody wants to see their own
number. Every first ask in this repo is for the artifact that produces
that number: a statement, a provider list.
