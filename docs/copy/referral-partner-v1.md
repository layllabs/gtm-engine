# Referral partner sequence (v1)

**Who:** businesses whose customers are merchants: restaurant suppliers,
POS resellers, bookkeepers, kitchen equipment repair, business associations.
**Goal:** a 15 minute call to set up a referral arrangement.
**Config:** [`config/sequences/referral-partner-v1.json`](../../config/sequences/referral-partner-v1.json)

## Why a partner lane exists

One signed restaurant supplier can introduce dozens of restaurants who
already trust them. Direct outbound wins one merchant per conversation.
Partner outbound can win one *channel* per conversation. The scoring model
reflects this: it weights fit and size over freshness, because a big
supplier is worth calling even if nothing happened to them this week.

## Day 0

> Subject: your customers' card fees
>
> Hi Greg,
>
> Saw Coastline Restaurant Supply already partners with a few vendors for your customers.
>
> A lot of those owners are overpaying on card processing and don't know it. I do free statement reviews. When one of your customers switches, you get a share of the revenue for as long as they stay. You don't sell anything, you just make the intro.
>
> Open to a 15 minute call to see if it fits?
>
> Joaquin

| Line | Why it's there |
|---|---|
| "your customers'" in the subject | Frames it around the people they care about keeping happy. |
| Opener about their existing partners | If they already refer vendors, this is a familiar ask, not a strange one. |
| "You don't sell anything" | The real objection is "I don't want to become your salesperson". Answered before it's raised. |
| "for as long as they stay" | Recurring, not one-time. That's the hook for a business owner. |
| 15 minute call | Partners are business-to-business. A short call is a normal ask here, unlike with a taqueria owner. |

## Day 4: call

Ask how many merchant customers they serve monthly and whether anyone ever
asks them about payments. Offer a one page referral card they can hand out.

## Day 9

> Subject: the one pager
>
> Greg, one more thought. Partners usually start by sending me the one customer who complains about fees the most. If the review saves them money, you look good and you get paid. Want me to send over the one pager?

Shrinks the commitment from "become a partner" to "send me one person".
Makes the partner look good to their own customer, which is the actual
motive.

## What I'd test next

- Opener variant that names a specific merchant type they serve
  ("your restaurant accounts") vs the generic version.
- Leading with the revenue share vs leading with "your customers are overpaying".
