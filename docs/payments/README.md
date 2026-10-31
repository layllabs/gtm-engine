# Payments GTM: the vertical resource

Everything in this repo was built selling card processing to local
businesses. This folder makes the vertical knowledge explicit and usable,
for two very different payments motions:

| | SMB merchant acquiring | Enterprise payment orchestration |
|---|---|---|
| Who sells it | an acquirer or ISO selling processing to owner-operated businesses | a platform that routes across PSPs for merchants with scale |
| Buyer | the owner | Head of Payments, VP Engineering, CFO |
| Trigger | fees, a new location, a new owner, a contract ending | a second PSP, a new country, an outage, auth-rate pressure |
| The conversation | the statement review | the routing diagram |
| Unit of value | basis points of markup on monthly volume | percentage points of authorization rate on annual volume |
| Sales cycle | days to weeks, often one call and a walk-in | months, technical evaluation, procurement |
| What this repo has | ICP `local-merchant`, sequence `local-merchant-v2`, the statement calculator | ICP `payments-enterprise-orchestration`, sequence `payments-orchestration-v1`, the merchant profile schema |

## Files

| File | What it is |
|---|---|
| [economics.md](economics.md) | How processing is priced, what a fair markup is, with public sources and the one number that matters per segment |
| [statement-review-playbook.md](statement-review-playbook.md) | The SMB sales conversation, step by step, using `python -m gtm statement` |
| [enterprise-orchestration-play.md](enterprise-orchestration-play.md) | The enterprise motion: signals, personas, discovery questions, the routing-diagram offer |
| [buyer-personas.md](buyer-personas.md) | Who you are talking to in each segment and what they actually care about |
| [objections.md](objections.md) | The objections that come up, what they mean, and the response that has worked |
| `schemas/merchant_statement.schema.json` | A normalized processing statement, the input to the calculator |
| `schemas/merchant_profile.schema.json` | Qualification fields for either segment |
| `gtm/statement.py` | The calculator: effective rate, pass-through vs markup, fair offer, flags, ETF payback |
| `config/icp/payments-enterprise-orchestration.json` | Scoring model for the enterprise lane |
| `config/sequences/payments-orchestration-v1.json` | The enterprise sequence |
| `data/sample_enterprise/` | A synthetic enterprise dataset; `python -m gtm run --data data/sample_enterprise --out examples/output_enterprise` |

## Run it

```
python -m gtm statement                      # review the sample statement
python -m gtm statement my_statement.json    # review yours, in the schema's shape
python -m gtm statement --markup-bps 25      # price a different offer
python -m gtm run --data data/sample_enterprise --out examples/output_enterprise
```

## Numbers policy

Public benchmark figures are cited with their source and the caveat that
most come from vendors. My own campaign numbers are not published here;
they are discussed in conversation. Sample statements and accounts are
synthetic and chosen to be typical, not copied from any merchant.
