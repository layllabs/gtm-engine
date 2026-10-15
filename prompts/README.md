# Prompts

Every LLM call in the engine has its prompt checked in here, versioned with
the code that calls it. No prompt lives only inside a tool's UI.

| Prompt | Workflow | Model | Output contract | Fallback if it fails |
|---|---|---|---|---|
| [reply-classifier.md](reply-classifier.md) | 04 reply handling | Sonnet | `schemas/reply.schema.json` | human review queue |
| [opener-writer.md](opener-writer.md) | 03 copy | Sonnet | one line of text | template opener from sequence config |
| [opener-qa.md](opener-qa.md) | 03 copy | Sonnet | `{"pass", "problems"}` | template opener |

Design rules:

1. **Deterministic first.** Rules handle what rules can (bounces, OOO,
   unsubscribes). The model only sees what is left. Cheaper, faster, and
   the rules double as an eval baseline.
2. **Every output has a schema.** Invalid output is discarded, never patched.
3. **Every model step has a non-model fallback.** The engine still runs
   if the API is down.
4. **Writer and reviewer are separate calls.**
