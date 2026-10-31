# The enterprise orchestration play

Selling payment orchestration to merchants with scale. A different buyer,
a different trigger, a different first ask than SMB. This is the motion
behind `config/icp/payments-enterprise-orchestration.json` and
`config/sequences/payments-orchestration-v1.json`.

## Who qualifies

Volume high enough that routing choices move revenue, and at least one of:

- Two or more PSPs already in the checkout (`multi_psp_detected`): they
  have the problem orchestration solves and are solving it by hand.
- Selling in more than one country (`new_market_launch`): local payment
  methods and local acquiring are where auth rates diverge.
- A payments hire open (`payments_hiring`): someone is about to own this
  and will want tooling, not a rebuild.
- A public outage or conversion post (`psp_outage_complaint`,
  `checkout_conversion_post`): the pain is stated.

Categories: marketplaces and travel first (multi-currency, high ticket,
high decline rates), then ecommerce, mobility, digital goods, subscription.

## Signals and where they come from

| Signal | Source | How it is detected |
|---|---|---|
| `multi_psp_detected` | web_scan | checkout page loads scripts or iframes from more than one PSP or wallet provider |
| `new_market_launch` | web_scan, press | new country in the store selector, a localized domain, a launch announcement |
| `payments_hiring` | job_boards | titles containing payments, checkout, billing platform, with engineering or product |
| `psp_outage_complaint` | status_pages, engineering blogs, social | a merchant-side post attributing downtime or failed payments to a provider |
| `checkout_conversion_post` | engineering blogs, talks | content from the merchant's team about conversion, retries, or decline handling |

These are read-only observations of public pages. Same sourcing rule as
the SMB lane: never quote, never name the platform, drop any source whose
terms prohibit it.

## Personas

| Persona | Cares about | Does not care about |
|---|---|---|
| Head of Payments | auth rate, cost per transaction, provider leverage, reconciliation | the vendor's provider count as a number |
| VP / Director Engineering | integration time per new PSP, failover, not owning routing logic in-house | pricing details |
| CFO / Finance | recovered revenue, fee consolidation, chargeback cost | technical architecture |
| Product (checkout) | conversion, local methods, one integration for every market | infrastructure |

The sequence targets the first two. Finance and product come in during
evaluation.

## The first ask

Not a demo. A **routing diagram**: send me your providers and countries,
I send back one page showing where first attempts, retries and local
methods would go. It costs them nothing, proves the vendor understands
their specific mix, and gives the Head of Payments an artifact to forward
internally. It is the enterprise equivalent of the statement review.

## Discovery questions, in order

1. When a transaction soft-declines today, what happens? (Nothing, or a
   retry on the same provider, or a retry elsewhere.)
2. Is authorization rate a tracked number? Who sees it and how often?
3. How long did the last PSP integration take, and who did it?
4. Which markets have the worst approval rates, and do you know why?
5. What breaks when a provider has an incident?
6. Who else would need to be in the room for a change to checkout?

Question 1 is the whole qualification. If the answer is "the customer
sees an error," the opportunity is real.

## What good looks like at each stage

| Stage | Exit criterion |
|---|---|
| Engaged | provider and country list received |
| Meeting | routing diagram reviewed with Head of Payments or engineering |
| Opportunity | auth-rate baseline shared, or agreement to measure it in a pilot |
| Pilot | one market or one provider pair routed through orchestration with before and after |
| Won | contract; the pilot number is the business case |

## What this lane does not do

- Cold-call engineering. Email and the diagram first; the call step in the
  sequence is for the payments lead.
- Promise an auth-rate lift. Public case studies exist (see
  `economics.md`); the pilot is where the merchant's own number comes from.
- Compete on provider count. The question is whether the providers they
  need are covered, not how many exist.

## Measuring the lane

Same scoreboard, same z-test, but the positive-reply definition should
include "sent provider list," since that is the first real step. Add it
as a `question`-class reply pattern once the lane has volume.
