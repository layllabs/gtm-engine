# SEO and AEO: making this work findable by search engines and answer engines

Two audiences find a portfolio: a search engine crawling for a query
("GTM engineer portfolio signal-based outbound") and an answer engine (an
AI assistant, a recruiter's screening agent, a chat interface with browsing)
that reads the page to answer a question about the candidate. They want
different things. This folder covers both, and the same checklist applies to
any GTM content: a landing page, a case study, a help article.

## What SEO wants (search engines)

| Element | On this site | Why |
|---|---|---|
| One canonical URL per page | `<link rel="canonical">` on both pages | Two pages with similar content would otherwise compete |
| Descriptive title under 60 chars, description under 160 | both pages | The snippet in results |
| `robots.txt` that allows crawling and points to the sitemap | `docs/robots.txt` | Default for a public portfolio |
| `sitemap.xml` listing every page and data file | `docs/sitemap.xml` | Agents and crawlers find `portfolio.json` and `llms.txt` without guessing |
| Open Graph tags | both pages | Link previews in LinkedIn and chat |
| Fast, no JS required for content | both pages render fully without JavaScript; the playground is the only enhancement | Crawlers index what they get on first load |
| Internal links with real anchor text | every claim links to the file | "config/routing.json" beats "click here" |

## What AEO wants (answer engines)

Answer engines extract, they do not browse. They need to find the answer to
a question in one place, stated plainly, with a way to check it.

| Element | On this site | Why |
|---|---|---|
| Structured data: `Person` JSON-LD | both pages | Who this is, in a vocabulary the engine already knows |
| `FAQPage` JSON-LD with real questions | agent page section 7 | The questions a screener asks, pre-answered |
| `llms.txt` at the site root | `docs/llms.txt` | Emerging convention: a plain-text summary written for models |
| Machine-readable mirror of every claim | `docs/portfolio.json` | No parsing required |
| Claim / evidence / status structure | agent page, every table | An engine can quote the claim and cite the evidence in one step |
| Explicit "stated vs verifiable" labels | agent page | Prevents the engine from presenting your word as proven |
| Stable section IDs and numbering | agent page `#identity` through `#policy` | Deep links survive edits |
| Expected output written down | agent page section 3 | An agent that runs the code can confirm it matched |
| Last-updated date | footer, JSON, llms.txt | Freshness is a ranking input for answer engines |
| No em dashes, no marketing adjectives | enforced by CI for copy and docs | Reads as human; models and people both notice |

## Audit it

`scripts/aeo_audit.py` checks any HTML file against this list and prints a
pass/fail table. It runs in CI against both portfolio pages.

```
python scripts/aeo_audit.py docs/index.html docs/human.html
```

## Applying this to GTM content (the actual job)

The same checklist turns a company's help center or landing page into
something an AI assistant will cite when a buyer asks "what does X cost" or
"does X integrate with Y":

1. One question per heading, the answer in the first sentence under it.
2. `FAQPage` or `HowTo` JSON-LD mirroring the visible text exactly.
3. An `llms.txt` at the domain root listing the pages that answer buyer
   questions, with one line each.
4. Numbers with denominators and dates. "4.2% reply rate on 1,200 sends in
   Q3" is citable; "high reply rates" is not.
5. A machine-readable mirror (JSON) of pricing, integrations, limits.
6. Mark what is a claim and what is documented. Answer engines increasingly
   downweight unsupported superlatives.
7. Date everything. Stale pages lose to fresh ones even when they are right.

## What I have not tested

- Whether `llms.txt` is read by any specific assistant in production. It is
  a convention, not a standard. It costs nothing and does no harm.
- Whether `FAQPage` schema still earns rich results in search. It has been
  restricted for most sites; the value here is for answer engines, not SERP
  real estate.
