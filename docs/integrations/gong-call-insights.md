# Gong call insights into the CRM

Pushing what was said on a call into fields a manager and the engine can
act on. Same pattern as reply handling: a schema-bound model call, a
deterministic fallback, a human in the loop before anything customer-facing.

## Flow

```mermaid
sequenceDiagram
    autonumber
    participant G as Gong
    participant E as Engine
    participant C as Claude
    participant S as Salesforce
    participant M as Manager
    G->>E: webhook: call processed (call id, account, transcript URL)
    E->>G: GET transcript + trackers
    E->>E: rules: duration, talk ratio, tracker hits, next-step phrase present
    E->>C: prompt (prompts/call-insights.md) + transcript
    C-->>E: JSON per schemas/call_insights.schema.json
    E->>E: validate; on failure fall back to rules-only summary
    E->>S: update Opportunity + Task; log Event on Account
    E->>M: weekly coaching digest: calls flagged by rubric
```

## What gets written

| Insight | Source | Salesforce field | Used for |
|---|---|---|---|
| Next step and date | model, rules fallback: "next step" phrase | `Opportunity.NextStep`, `Task` | Pipeline hygiene; no call without a next step |
| Objections raised | model | `Opportunity.Objections__c` (multi-picklist) | Battlecard priority, win/loss |
| Competitor mentioned | Gong trackers | `Opportunity.Competitor__c` | Competitive reporting |
| Decision maker on call | model | `Opportunity.DM_Confirmed__c` | Forecast confidence |
| Statement received / promised | model | `Opportunity.Statement_Status__c` | The engine's own conversion step |
| Talk ratio, longest monologue | Gong stats | `Event.Talk_Ratio__c`, `Event.Longest_Monologue__c` | Coaching |
| Rubric score (1 to 5 per stage) | model against a written rubric | `Event.Call_Score__c`, `Event.Call_Score_Notes__c` | Coaching digest; the rep sees it too |

## Guardrails

- Model output must validate against the schema or it is discarded; the
  rules-only summary (duration, trackers, next-step phrase found or not)
  still writes.
- Nothing customer-facing is generated here. Follow-up email drafts are a
  separate step with approval.
- Rubric scores are visible to the rep, never hidden. Coaching from a
  score the rep cannot see is not coaching.
- Transcripts are not stored in the shadow CRM; only the extracted fields
  and the Gong call id.

## Prompt and schema

- `prompts/call-insights.md`
- `schemas/call_insights.schema.json`

## Status

Spec plus prompt plus schema. Not wired in the public repo; the Gong
webhook and Salesforce writes live with the employer's credentials. The
reply-handling path (`gtm/replies.py`) is the same shape, working.
