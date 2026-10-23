-- Questions I ask the shadow CRM (examples/output/engine.db) after a run.
-- Run all of them: python -m gtm sql
-- Run one:         python -m gtm sql --name signals_to_meetings

-- name: funnel_by_tier
-- How many accounts in each tier, and what action they got.
SELECT a.tier, r.action, COUNT(*) AS accounts
FROM accounts a JOIN routes r USING (account_id)
GROUP BY a.tier, r.action
ORDER BY a.tier, accounts DESC;

-- name: signals_to_meetings
-- Which signal types turn into meetings. The number that should set signal weights.
SELECT s.type AS signal_type,
       COUNT(DISTINCT s.account_id) AS accounts_with_signal,
       COUNT(DISTINCT CASE WHEN e.to_state = 'meeting' THEN e.account_id END) AS reached_meeting
FROM signals s
LEFT JOIN events e ON e.account_id = s.account_id
GROUP BY s.type
ORDER BY reached_meeting DESC, accounts_with_signal DESC;

-- name: owner_load
-- Accounts and open tasks per rep, so territory rules can be rebalanced.
SELECT COALESCE(a.owner, 'unassigned') AS owner,
       COUNT(*) AS accounts,
       SUM(CASE WHEN a.tier = 'A' THEN 1 ELSE 0 END) AS tier_a,
       SUM(CASE WHEN r.task IS NOT NULL THEN 1 ELSE 0 END) AS open_tasks
FROM accounts a JOIN routes r USING (account_id)
GROUP BY a.owner
ORDER BY accounts DESC;

-- name: reply_outcomes
-- Reply labels and where each account ended up.
SELECT rp.label, a.state_current, COUNT(*) AS n
FROM replies rp LEFT JOIN accounts a USING (account_id)
GROUP BY rp.label, a.state_current
ORDER BY n DESC;

-- name: variant_split
-- Day-0 variant assignment is hash-stable; confirm the split is roughly even.
SELECT sequence, variant, COUNT(DISTINCT account_id) AS accounts
FROM touches WHERE day = 0
GROUP BY sequence, variant;

-- name: stale_sequenced
-- Accounts sequenced with no state change since: the follow-up list.
SELECT a.business_name, a.owner, MAX(e.at) AS last_event
FROM accounts a JOIN events e USING (account_id)
WHERE a.state_current = 'sequenced'
GROUP BY a.account_id
ORDER BY last_event;

-- name: account_history
-- Full event trail for one account; parameter: the account's business name.
SELECT e.at, e.from_state, e.to_state, e.reason
FROM events e JOIN accounts a USING (account_id)
WHERE a.business_name LIKE '%Harbor Brake%'
ORDER BY e.at;

-- name: lint_blocks
-- Any touch that failed lint and why. Should be empty.
SELECT account_id, sequence, day, lint
FROM touches WHERE lint != '[]';

-- name: dq_reasons
-- Why accounts were disqualified, grouped.
SELECT reasons, COUNT(*) AS n
FROM accounts WHERE tier = 'DQ'
GROUP BY reasons ORDER BY n DESC;
