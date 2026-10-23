---
name: connect-tools
description: Connect the GTM engine to a sales tool (GitHub, Smartlead, Outreach, Salesforce, HubSpot, Apollo, ZeroBounce, Clay, Anthropic) or add a new one. Use when the user says "connect X", "hook up X", "add X to the engine", "is X working", or "which tools are connected".
---

# Connect tools

The engine talks to outside tools through one registry
(`gtm/integrations/registry.py`). Every connector declares its credential
env var, auth style, base URL, a read-only probe endpoint, and rate limit.
`python -m gtm connect` shows what is configured and proves each
credential with one GET. Nothing in this skill writes to any tool.

## Check what is connected

```
python -m gtm connect              # probe every configured tool
python -m gtm connect --no-probe   # just show which env vars are set
python -m gtm connect --json       # machine readable, for agents
```

Status meanings: `OK` credential works; `AUTH` credential rejected (401/403);
`ERR` network or non-auth HTTP error; `SET` configured but not probed;
`--` env var missing; `SKIP` tool has no safe probe endpoint (Clay).

## Connect an existing tool

1. Copy `.env.example` to `.env` if it does not exist. `.env` is gitignored.
2. Get the credential from the tool. Where to find it:
   - **GitHub**: Settings > Developer settings > Fine-grained tokens. Scope
     to the one repo, Contents read/write. Expires. `GITHUB_TOKEN`.
   - **Smartlead**: Settings > API. `SMARTLEAD_API_KEY`.
   - **Outreach**: OAuth app in the Outreach admin, then a token exchange.
     The engine expects the resulting access token in
     `OUTREACH_ACCESS_TOKEN`; refresh is the caller's job.
   - **Salesforce**: Connected App with OAuth, or `sf org display` from the
     Salesforce CLI, gives an access token and instance URL.
     `SFDC_ACCESS_TOKEN`, `SFDC_INSTANCE_URL`.
   - **HubSpot**: Settings > Integrations > Private Apps, scopes
     `crm.objects.contacts.read` at minimum. `HUBSPOT_ACCESS_TOKEN`.
   - **Apollo**: Settings > Integrations > API. `APOLLO_API_KEY`.
   - **ZeroBounce**: dashboard API section. `ZEROBOUNCE_API_KEY`.
   - **Clay**: a table webhook URL, no key. `CLAY_WEBHOOK_URL`.
   - **Anthropic**: console API keys. `ANTHROPIC_API_KEY`.
3. Put it in `.env`. Run `python -m gtm connect`. Expect `OK` for that row.
4. If `AUTH`: the key is wrong, expired, or lacks scope. Re-check scope first;
   most failures are scope, not typos.
5. Never paste a credential into chat, a commit, a doc, or an issue. If one
   leaks, revoke it at the source before anything else.

## Add a new tool

1. Add one `Connector(...)` to `REGISTRY` in `gtm/integrations/registry.py`:
   key, name, role in the engine, env var(s), auth style (`bearer`,
   `x-api-key`, `api-key-header`, `token`, `query-api-key`, `none`),
   base URL, a cheap GET that proves the credential (a "me", "limits", or
   "list 1" endpoint), docs link, rate limit.
2. Add the env var to `.env.example` with a comment.
3. Add the "where to find the credential" line to this file.
4. Run `python -m gtm connect --no-probe` and confirm the row appears.
5. If the tool needs a new auth style, add one branch to
   `Connector.headers()` or `probe_url()`. Keep it to headers or a query
   parameter; anything needing a signing step belongs in its own module.

## Rules

- Probes are read-only GETs. Adding a connector never adds a write.
- One tool per role in production: one sequencer, one CRM. The registry
  lists alternatives so switching is a config change, not a rewrite.
- Rate limits are recorded so batch jobs can be sized before they run.
- A connector without a safe probe is marked `SKIP`, not faked.
