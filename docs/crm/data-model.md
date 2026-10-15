# CRM data model

Two layers:

- **System of record CRM** (Salesforce, HubSpot or Attio): accounts,
  contacts, opportunities, owner. What leadership reports on.
- **Shadow CRM** (SQLite, `gtm/store.py`): everything the engine needs
  that would otherwise mean asking RevOps for a new custom field every week.

```mermaid
erDiagram
    ACCOUNT ||--o{ SIGNAL : "evidenced by"
    ACCOUNT ||--|| ROUTE : "gets"
    ACCOUNT ||--o{ TOUCH : "receives"
    ACCOUNT ||--o{ REPLY : "sends"
    ACCOUNT ||--o{ EVENT : "logs"
    ACCOUNT }o--|| ICP : "scored against"
    TOUCH }o--|| SEQUENCE : "step of"

    ACCOUNT {
        text account_id PK "sha1(name+city)"
        text business_name
        text category
        text city
        text state
        text email
        text phone
        text icp FK
        text lane "direct or partner"
        real score
        text tier "A B C D DQ"
        json components "5 score parts"
        json reasons "why, in words"
        text state_current "lifecycle state"
    }
    SIGNAL {
        int id PK
        text account_id FK
        text type
        date date
        text source
        text source_id "trace to origin"
        text text "raw evidence"
    }
    ROUTE {
        text account_id PK
        text rule "which routing rule fired"
        text action
        text sequence
        json task "type, due, note"
        text suppression_reason
    }
    TOUCH {
        int id PK
        text account_id FK
        text sequence
        text variant
        int day
        text channel
        text subject
        text body
        json lint "empty means clean"
    }
    REPLY {
        text id PK
        text account_id FK
        text label
        real confidence
        text next_action
        json extra "follow_up_on, resume_on, referred_email"
    }
    EVENT {
        int id PK
        text at
        text account_id FK
        text from_state
        text to_state
        text reason
    }
    ICP {
        text id PK
        text lane
        json weights
        json tiers
    }
    SEQUENCE {
        text id PK
        text lane
        json steps
    }
```

## What syncs to the system of record

Only what a manager or another rep needs:

| Shadow field | CRM field | Why it syncs |
|---|---|---|
| `tier` | Account priority picklist | Drives views and territory reports |
| top `reasons` | Account description, first line | Context for anyone who opens the record |
| `state_current` in engaged / meeting | Opportunity created | Pipeline lives in the CRM |
| reply `follow_up_on` | Task with due date | Shows on the rep's task list |
| suppression | Do-not-contact checkbox | Compliance must be visible everywhere |

Everything else (score components, every signal, every draft, every lint
result, every state change) stays local. It is queryable with plain SQL:

```sql
-- Which signal types turn into meetings?
SELECT s.type, COUNT(DISTINCT e.account_id) AS meetings
FROM events e JOIN signals s USING (account_id)
WHERE e.to_state = 'meeting'
GROUP BY s.type ORDER BY meetings DESC;

-- Accounts that went quiet: sequenced more than 14 days, no reply
SELECT a.business_name, MAX(e.at) AS since
FROM accounts a JOIN events e USING (account_id)
WHERE a.state_current = 'sequenced'
GROUP BY a.account_id HAVING since < date('now', '-14 days');
```

## Keys and identity

- `account_id` is derived (sha1 of normalized name + city), so the same
  business gets the same ID on every run without a lookup service.
- `signal.source_id` keeps the link back to the original permit, filing,
  post or listing for audit.
- Replies match accounts by sender email. Bounces come from a mailer
  daemon, so in production they match by original message ID instead.
