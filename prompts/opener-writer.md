# Prompt: personalized opener

**Used in:** workflow 03, after routing, before lint.
**Model:** Sonnet writes, a second Sonnet call reviews (`opener-qa.md`).
**Fallback:** if either call fails or QA rejects twice, the template opener
from `config/sequences/*.json` is used. A draft always exists.

---

Write the first line of a cold email to the owner of a local business.

You get the account record and the signal that put it in today's queue.
Your line should prove we noticed something specific and real, then stop.

Account:
```json
{{account_json}}
```

Signal evidence:
```
{{signal_text}}
```

Constraints:
- One or two sentences. Under 30 words total.
- Reference the signal concretely. "Saw the new permit for the Pine Ave
  spot" beats "Saw you're growing".
- No compliments that could apply to any business.
- No em dashes, en dashes, exclamation marks, or emojis.
- Do not mention payments, fees, or what we sell. The rest of the email
  does that.
- Do not invent facts. If the evidence is thin, write a plain line about
  the city and category instead.
- If the signal came from a public post by the owner (Reddit, Craigslist),
  reference the topic, never quote them or name the platform.

Return only the line.
