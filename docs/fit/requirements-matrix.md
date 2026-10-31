# GTM Engineer requirements, mapped to this repo

Three public GTM Engineer postings I applied to in October 2026 (a
vertical-SaaS company, a restaurant-tech company, a payments company),
with every recurring requirement and where in this repo it is
demonstrated. Status uses the same labels as the portfolio pages:
**verifiable** (open the file, run the command) or **stated** (my word).

## Required

| Requirement (as the postings phrase it) | Where | Status |
|---|---|---|
| Own automation workflows across CRM, enrichment, sequencer, conversation intelligence | `gtm/pipeline.py`, `gtm/integrations/registry.py`, `docs/workflows/` | verifiable |
| AI-driven enrichment; waterfall sourcing; custom logic for SMB websites | `config/enrichment.json`, `gtm/enrich.py`, coverage table on the scoreboard | verifiable |
| GPT/LLM-driven outbound personalization frameworks with evals, guardrails, human review | `prompts/`, `schemas/`, `docs/ai-guardrails.md`, `data/sample/reply_eval.jsonl` | verifiable |
| Routing logic, enrichment standards, scoring, with Sales and Marketing Ops | `config/routing.json`, `config/icp/*.json`, `docs/workflows/02`, `03` | verifiable |
| Automatic territory assignment | `config/territories.json`, `gtm/territory.py`, `owner_load` query | verifiable |
| Inbound speed-to-lead, routing, attribution | `gtm/inbound.py`: SLA by intent, owner, first-touch attribution captured once | verifiable |
| Push Gong call insights into Salesforce | `docs/integrations/gong-call-insights.md`, `prompts/call-insights.md`, `schemas/call_insights.schema.json` | spec, not wired publicly |
| Deep Salesforce experience: object relationships, lifecycle design | `docs/crm/salesforce-field-map.md`, `docs/crm/lifecycle.md`, `docs/crm/data-model.md` | verifiable (design); stated (years of use) |
| Sender infrastructure: domain strategy, inbox rotation, warmup | `docs/runbooks/sending-domain-setup.md`, `config/deliverability.json`, `gtm/health.py` | verifiable |
| Monitoring, alerting, error handling in integration workflows | `docs/runbooks/monitoring-and-alerting.md` | verifiable (design) |
| Zapier / Workato / n8n / Make | `integrations/n8n/run-the-engine.json` (importable), ADR 001 on when to use it | verifiable; Gumloop and n8n use stated |
| Clay: multi-step tables, waterfalls, formulas | `gtm/enrich.py` is the same shape as a Clay table; Clay listed in the registry; hands-on use | stated (resume) |
| Signal-based and ABM motions; intent data | `docs/signals.md`, ADR 003 | verifiable |
| APIs, webhooks, scripting in Python or JS, JSON | whole repo; `scripts/`, `docs/rules.json`, n8n Code node | verifiable |
| Data hygiene, dedupe, systems thinking | `gtm/dedupe.py`, lifecycle state machine, suppression | verifiable |
| Document processes, write SOPs, record walkthroughs | `docs/runbooks/`, `docs/workflows/`, `skills/connect-tools/SKILL.md`; Loom pending | verifiable; Loom stated |
| Tie automation to seller productivity and pipeline | scoreboard: today's call list, `signals_to_meetings` query, `owner_load` | verifiable (mechanism); numbers stated |
| High-velocity, low-ACV motion, thousands of accounts per market | the ICP is local merchants; attainment at Shopify and LogicMonitor | stated |
| Shipped AI workflows that reach real customers | engine in production use | stated |

## Listed as a plus

| Plus | Where | Status |
|---|---|---|
| Strong SQL and working Python | `docs/sql/analysis.sql`, `python -m gtm sql`; about 1,800 lines of stdlib Python | verifiable |
| Local business or multi-location data | the whole ICP; dedupe across permits, filings, maps | verifiable |
| Restaurant tech, hospitality, vertical SaaS background | hospitality vertical at Medallia; restaurants as primary ICP | stated |
| Fintech, payments, embedded finance | `docs/payments/`: processing economics with sources, statement-review calculator (`python -m gtm statement`), enterprise orchestration lane with its own ICP, signals and sequence, statement and merchant-profile schemas | verifiable |
| Apollo, Demandbase, Gong, Chili Piper | Apollo in registry; Gong spec; territory module is the Chili Piper / LeanData equivalent; Demandbase not covered | partial |
| Looker, Tableau, attribution tools | attribution fields captured in `gtm/inbound.py`; dashboards built internally (Outbound Center) | stated |
| Salesforce admin | field map and validation rules designed; not certified | stated |
| Building without a large team | one person built this | verifiable |
| Global markets | not covered | gap |
| Marketo or marketing automation | not covered | gap |
| PPC, LinkedIn or Reddit ads, ABM ad platforms | not covered | gap |
| Post-sale: onboarding automation, account health scoring | not covered; same scoring pattern would apply | gap |

## How to read the gaps

Four items are plain gaps and I say so rather than stretch. Marketing
automation and paid ads are the biggest; both are adjacent to what is here
(the signal and routing layers do not care whether the trigger is a permit
or an ad click) but I have not run them.
