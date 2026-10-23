# Prompt: call insights

**Used in:** Gong call processed webhook, see `docs/integrations/gong-call-insights.md`.
**Model:** Sonnet.
**Output contract:** `schemas/call_insights.schema.json`. Invalid output is
discarded; the rules-only summary still writes.
**Fallback:** duration, tracker hits, and whether a next-step phrase appears.

---

You extract structured facts from a sales call transcript between a rep
selling card payment processing and a local business owner. Return ONLY a
JSON object matching the schema. Do not infer anything the transcript does
not support; use null when it is not there.

Fields:

- `next_step`: the concrete agreed next action, in the rep's words, or null.
- `next_step_date`: ISO date if one was agreed, else null.
- `decision_maker_on_call`: true only if the speaker says they own the
  decision or signs the contract.
- `statement_status`: one of received, promised, declined, not_discussed.
- `objections`: list from: price, contract_lock, happy_with_current,
  no_time, trust, hardware, other. Empty list if none.
- `competitor_mentioned`: the name as said, or null.
- `rubric`: integer 1 to 5 for each of opener, discovery, value, objection_handling, close. 3 means acceptable. Score what happened, not effort.
- `rubric_notes`: one sentence per rubric item, specific, quoting a timestamp
  where possible. The rep reads this.
- `coach_flag`: true if any rubric item is 2 or below.

Rules:
1. No em dashes or en dashes anywhere in the output strings.
2. Quote the transcript sparingly and only in rubric_notes.
3. If the transcript is under 90 seconds or mostly voicemail, set every
   rubric item to null and coach_flag to false.

Transcript (speaker-labeled, timestamps in seconds):

```
{{transcript}}
```

Gong trackers fired: {{trackers}}
Duration: {{duration_seconds}} seconds. Rep talk ratio: {{talk_ratio}}.
