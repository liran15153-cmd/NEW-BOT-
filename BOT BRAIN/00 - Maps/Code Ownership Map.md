---
type: map
status: current
source: code
---

# Code Ownership Map

This map defines where responsibilities belong. Future changes should preserve these boundaries unless a deliberate architecture change is made.

## Ownership

- `app/api`: [[API Layer]], thin HTTP routes only.
- `app/ai`: [[AI Layer]], bot orchestration, parsing, policy, planning, response construction.
- `app/dialogue`: [[Dialogue Layer]], short-lived conversation continuation.
- `app/financial`: [[Financial Layer]], structured contracts, demo facts, deterministic decisions.
- `app/core`: settings and small shared app helpers.
- `app/tester`: local manual QA surface.

## How To Use This Map During Development

Before editing a file, identify which layer owns the behavior. If the change is about "what does the user see?", it probably belongs in [[Hebrew Response Builder]]. If it is about "is this request allowed?", it belongs in [[Assistant Response Policy]]. If it is about "what is the risk level?", it belongs in [[Decision Engine]]. If it is about "what amount did the user mention?", it belongs in [[Parameter Extractor]].

This prevents a common failure mode: putting quick fixes in `chat_router.py` because it is central. The router should coordinate, not accumulate hidden business rules.

## Signs A Change Is In The Wrong Layer

- A FastAPI route starts importing regex or financial decision classes.
- A financial tool returns complete user-facing sentences.
- The decision engine contains Hebrew copy.
- The response builder calculates core money logic.
- Dialogue state stores full answers or long-term user facts.

## Forbidden Drift

- Do not put business logic in FastAPI routes.
- Do not put user-facing Hebrew copy in financial tools or decision logic.
- Do not put persistence, WhatsApp, Open Banking, Supabase, or LLM adapters into the current bot-brain path prematurely.

## Related Notes

- [[Architecture Principles]]
- [[How To Work On This Project]]
- [[Change Checklist]]
