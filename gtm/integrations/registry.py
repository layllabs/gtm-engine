"""Connector registry: one place that knows how to reach every tool.

Each connector declares how it authenticates, which environment variable
holds the credential, and a cheap read-only endpoint that proves the
credential works. `python -m gtm connect` walks the registry, reports
which tools are configured, and probes the ones that are.

Nothing here writes to any tool. Probes are GET requests to list or
"whoami" style endpoints. Adding a tool is adding a dict, not code.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass
class Connector:
    key: str
    name: str
    role: str                      # what this tool does in the engine
    env: list[str]                 # required env vars
    auth: str                      # how the credential is sent
    base_url: str
    probe_path: str                # cheap read-only endpoint
    docs: str
    rate_limit: str = ""
    optional_env: list[str] = field(default_factory=list)

    def configured(self) -> bool:
        return all(os.environ.get(v) for v in self.env)

    def headers(self) -> dict[str, str]:
        h = {"Accept": "application/json", "User-Agent": "gtm-engine/0.3"}
        if self.auth == "bearer":
            h["Authorization"] = f"Bearer {os.environ[self.env[0]]}"
        elif self.auth == "x-api-key":
            h["X-Api-Key"] = os.environ[self.env[0]]
        elif self.auth == "api-key-header":
            h["api-key"] = os.environ[self.env[0]]
        elif self.auth == "token":
            h["Authorization"] = f"token {os.environ[self.env[0]]}"
        return h

    def probe_url(self) -> str:
        base = os.environ.get(self.optional_env[0], self.base_url) if self.optional_env else self.base_url
        url = base.rstrip("/") + self.probe_path
        if self.auth == "query-api-key":
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}api_key={os.environ[self.env[0]]}"
        return url


REGISTRY: list[Connector] = [
    Connector(
        key="github", name="GitHub", role="source of truth for engine config and docs; CI runs here",
        env=["GITHUB_TOKEN"], auth="bearer", base_url="https://api.github.com", probe_path="/user",
        docs="https://docs.github.com/en/rest", rate_limit="5,000 req/hour authenticated",
    ),
    Connector(
        key="smartlead", name="Smartlead", role="cold email sequencer and mailbox rotation (alternative to Apollo sequences)",
        env=["SMARTLEAD_API_KEY"], auth="query-api-key", base_url="https://server.smartlead.ai/api/v1",
        probe_path="/campaigns", docs="https://api.smartlead.ai", rate_limit="60 req/min",
    ),
    Connector(
        key="outreach", name="Outreach", role="sequencer used by larger sales teams; OAuth, not a static key",
        env=["OUTREACH_ACCESS_TOKEN"], auth="bearer", base_url="https://api.outreach.io/api/v2",
        probe_path="/users?page[size]=1", docs="https://developers.outreach.io", rate_limit="10,000 req/hour per user",
    ),
    Connector(
        key="salesforce", name="Salesforce", role="system of record for accounts and opportunities",
        env=["SFDC_ACCESS_TOKEN", "SFDC_INSTANCE_URL"], auth="bearer", base_url="",
        probe_path="/services/data/v60.0/limits", docs="https://developer.salesforce.com/docs/apis",
        rate_limit="daily API request allocation per org", optional_env=["SFDC_INSTANCE_URL"],
    ),
    Connector(
        key="hubspot", name="HubSpot", role="CRM for teams not on Salesforce",
        env=["HUBSPOT_ACCESS_TOKEN"], auth="bearer", base_url="https://api.hubapi.com",
        probe_path="/crm/v3/objects/contacts?limit=1", docs="https://developers.hubspot.com/docs/api/overview",
        rate_limit="100 req / 10 sec private app",
    ),
    Connector(
        key="apollo", name="Apollo", role="contact data and sequencing in the current stack",
        env=["APOLLO_API_KEY"], auth="x-api-key", base_url="https://api.apollo.io/api/v1",
        probe_path="/auth/health", docs="https://docs.apollo.io", rate_limit="plan dependent, per minute and per day",
    ),
    Connector(
        key="zerobounce", name="ZeroBounce", role="email verification before enrollment",
        env=["ZEROBOUNCE_API_KEY"], auth="query-api-key", base_url="https://api.zerobounce.net/v2",
        probe_path="/getcredits", docs="https://www.zerobounce.net/docs", rate_limit="credits based",
    ),
    Connector(
        key="clay", name="Clay", role="enrichment and waterfall lookups; webhook driven, no public read API for probing",
        env=["CLAY_WEBHOOK_URL"], auth="none", base_url="", probe_path="",
        docs="https://www.clay.com/university", rate_limit="per table",
    ),
    Connector(
        key="anthropic", name="Anthropic", role="Claude for opener writing, QA, and low-confidence reply classification",
        env=["ANTHROPIC_API_KEY"], auth="api-key-header", base_url="https://api.anthropic.com/v1",
        probe_path="/models", docs="https://docs.anthropic.com", rate_limit="tier based",
    ),
]


def probe(c: Connector, timeout: float = 8.0) -> tuple[str, str]:
    """Returns (status, detail). status in: ok, auth_failed, error, skipped."""
    if not c.probe_path:
        return "skipped", "no read-only probe endpoint for this tool"
    req = urllib.request.Request(c.probe_url(), headers=c.headers())
    if c.key == "anthropic":
        req.add_header("anthropic-version", "2023-06-01")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(20000).decode("utf-8", "replace")
            try:
                parsed = json.loads(body)
                shape = f"keys {list(parsed)[:4]}" if isinstance(parsed, dict) else f"list of {len(parsed)}"
            except ValueError:
                shape = f"{len(body)} bytes, not JSON"
            return "ok", f"HTTP {r.status}, {shape}"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return "auth_failed", f"HTTP {e.code}: credential rejected"
        return "error", f"HTTP {e.code}"
    except Exception as e:  # network, DNS, timeout
        return "error", type(e).__name__


def report(live: bool = True) -> list[dict]:
    rows = []
    for c in REGISTRY:
        row = {"key": c.key, "name": c.name, "role": c.role, "env": c.env, "configured": c.configured()}
        if c.configured() and live:
            row["status"], row["detail"] = probe(c)
        elif c.configured():
            row["status"], row["detail"] = "configured", "not probed"
        else:
            row["status"], row["detail"] = "missing", "set " + ", ".join(c.env)
        rows.append(row)
    return rows
