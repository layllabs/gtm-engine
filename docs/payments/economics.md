# Payments economics, as a seller needs to know them

## SMB card processing: where the money goes

A merchant's processing cost has three layers. Only one is negotiable.

| Layer | Who gets it | Negotiable? | Typical size, card-present SMB |
|---|---|---|---|
| Interchange | the cardholder's issuing bank | no, set by the card networks by card type and how it was presented | roughly 1.5% to 2.2% of volume, higher for rewards and corporate cards, higher still for card-not-present |
| Assessments | the card network (Visa, Mastercard, Discover, Amex) | no | roughly 0.13% to 0.15% of volume plus small per-item fees |
| Processor markup | the acquirer / ISO / processor | yes, entirely | anywhere from 0.03% to over 1.0% of volume, plus per-item, plus monthly fees |

The processor's markup is the whole conversation. Everything else is the
same at any processor.

### What a fair markup looks like

One merchant-consulting firm's published case study of a card-present
practice showed a 2.18% effective rate with interchange and assessments at
1.86%, processor percentage markup of 0.20% + $0.10 per transaction, and
calls that "a good deal." The same source says the lowest markup it has
seen is 0.03% + $0.03 for a $250M+ ecommerce merchant, and that 3% to 4%
effective "shouldn't be accepted as normal" ([Merchant Cost Consulting][mcc]).

The engine's calculator uses 20 bps + $0.10 as the default fair offer
for card-present SMB (`gtm/statement.py`, `DEFAULT_OFFER`) and flags
anything over 50 bps all-in. Those are my working thresholds, informed by
the source above and by statements I have reviewed; they are config, not
law.

### Pricing models and what they hide

| Model | What the statement shows | What it hides |
|---|---|---|
| Interchange-plus | interchange, assessments, markup as separate lines | nothing; this is the one you can audit |
| Tiered (qualified / mid / non-qualified) | three blended rates | which transactions got downgraded and why; the markup is inside the tiers |
| Flat rate (2.9% + $0.30 style) | one rate | the spread between the flat rate and actual interchange, which is large on debit and small-ticket |
| Subscription | monthly fee plus pass-through | usually nothing; can be good at volume, bad under about $10k/month |

The calculator refuses to estimate savings on tiered or flat-rate
statements. The honest move is to ask for interchange detail or quote
interchange-plus and let the merchant compare.

### The junk fee list

Fees that are often on the statement and often avoidable: PCI
non-compliance (complete the SAQ), equipment lease (buy the terminal),
statement fee, batch fee, annual fee, "regulatory" fee, early termination
fee on auto-renewing contracts. The calculator flags PCI and equipment
individually because they are the two owners notice first.

### The number that matters

**Effective rate** = total fees / volume, all-in. Owners guess theirs low by
about a point. Computing it from one statement and reading it back is the
whole first call. The second number is **markup in basis points over
interchange**, because that is the only part that changes with a switch.

## Enterprise payment orchestration: a different unit of value

At scale the cost conversation flips from fees to revenue. The merchant
already has negotiated rates; what they lose is approved transactions.

- **Authorization rate** is the metric. One orchestration vendor's case
  study reports a 2.8 percentage point authorization-rate rise over four
  months after adding smart routing and dual-bank failover
  ([Chargeback.io roundup citing GR4VY][cb]). The roundup also notes that
  results vary by provider mix and market, which is the honest caveat.
- On $100M in annual volume, one point of authorization rate is $1M of
  revenue the merchant already earned and did not capture. That is the
  size of the conversation.
- **When orchestration makes sense:** the same roundup's working rule is
  "add orchestration once you run 2 or more processors," with volume high
  enough that routing choice matters. That is why `multi_psp_detected` is
  the strongest signal in `config/icp/payments-enterprise-orchestration.json`.
- **Who buys it:** mid-market and enterprise merchants; vendors position by
  geography breadth, provider count, and risk tolerance. Yuno is described
  in that roundup as best for enterprise buyers with many geographies;
  pricing not public.

### Enterprise unit of value, as the calculator would frame it

```
annual_volume x (target_auth_rate - current_auth_rate) = recovered revenue
```

Nobody will give you the current auth rate on a cold call. The sequence
asks a smaller question instead: what happens on a soft decline today.

## Sources

- [mcc]: Merchant Cost Consulting, "2% credit card processing rate," case study with itemized fees. Marketing content from a consulting firm; one merchant, not an average.
- [cb]: Chargeback.io, "Best payment orchestration platforms compared," 2026. Vendor roundup from a chargeback-alerts company; the auth-rate figure is from GR4VY's Baby Bunting case.

[mcc]: https://merchantcostconsulting.com/lower-credit-card-processing-fees/2-percent-credit-card-processing-rate/
[cb]: https://www.chargeback.io/blog/best-payment-orchestration-platforms

Both are vendor sources. Independent interchange schedules are published
by the networks; the numbers above are consistent with them for US
card-present retail but are not pulled from the schedules directly.
