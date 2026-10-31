# The statement review

In SMB payments the statement review is the meeting. It is the thing the
sequence asks for, the thing the walk-in asks for, and the thing that
turns a cold conversation into a specific one. This is how I run it.

## Getting the statement

- Ask for one month, page one is enough. A photo from their phone is fine.
- Say what they will get back: their effective rate, what is pass-through,
  what is markup, in writing, the same day. No pitch until they have seen it.
- If they say "I don't have it handy," the processor's online portal has
  it; offer to wait on the phone while they log in.

## Normalizing it

Fill `schemas/merchant_statement.schema.json`. Thirty seconds on an
interchange-plus statement, longer on tiered. What goes where:

| On the statement | Field |
|---|---|
| Total sales, gross volume, net sales | `volume` |
| Number of transactions, items, sales count | `transactions` |
| Interchange, "IC", issuer fees | `fees.interchange` |
| Dues and assessments, network fees, Visa/MC/Disc fees | `fees.assessments` |
| Discount rate, processing fee, rate x volume | `fees.processor_percentage` |
| Per item, transaction fee, auth fee | `fees.processor_per_item` |
| Statement fee, monthly fee, gateway, batch | `fees.monthly_fixed` |
| PCI compliance, PCI non-compliance | `fees.pci` |
| Equipment lease, terminal rental | `fees.equipment` |
| Anything else | `fees.other` |

If interchange is not a line, set `pricing_model` to `tiered` or
`flat_rate` and leave `fees.interchange` null. Do not guess it.

## Running it

```
python -m gtm statement path/to/statement.json
```

Read the output back to the owner in this order:

1. **Their effective rate.** "You paid $1,706 on $48,250. That's 3.54%."
   Pause. Most owners thought it was 2-something.
2. **What is not negotiable.** "$959 of that is interchange and card
   brand fees. Same at any processor. Nobody can beat that."
3. **What is.** "The other $747 is the processor. That's 155 basis points
   all-in. A fair number for a shop like yours is 20 to 30 on the
   percentage, and a dime a transaction."
4. **The offer, in their dollars.** "Same pass-through, 20 and a dime:
   $1,279 a month. $428 less than this month. About $5,100 a year."
5. **The flags.** PCI fee, equipment lease, auto-renew, ETF and its payback.
   "The $495 cancellation fee is covered in six weeks."
6. **The ask.** Not "sign." "Want me to put that in writing against this
   exact statement so you can show whoever you want?"

## What not to do

- Do not promise savings on a tiered or flat-rate statement. Say what you
  can see and what you need to see.
- Do not disparage the current processor by name. The numbers do it.
- Do not quote a rate before you have the statement. A rate without a
  statement is a guess, and the owner has heard a hundred of them.
- Do not round in your favor. Round against yourself; it builds trust and
  the difference is still large.

## After the call

- Write the review up from the calculator output. One page. Their numbers,
  the offer, the flags, the contract dates.
- Statement received moves the opportunity to `statement_status =
  received` (see the Gong insights field map); the engine's lifecycle moves
  the account to `meeting`.
- If they want to wait for the contract end, set the follow-up task for 60
  days before `contract.end_date`, which is usually the cancellation
  window.
