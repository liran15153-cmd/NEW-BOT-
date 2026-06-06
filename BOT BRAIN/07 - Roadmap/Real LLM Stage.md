---
type: roadmap
status: future
source: docs
---

# Real LLM Stage

A real LLM is not currently needed for the deterministic MVP.

## Prerequisites

- stable deterministic policy layer
- clear prompt-injection boundaries
- explicit privacy review
- structured output validation
- tests for unsafe output
- no secret exposure
- logging and retention rules

## Possible Good Use

A real LLM may eventually help with flexible natural-language understanding or answer polish. It should not be the source of financial facts or final policy decisions.

## Architecture Rule

If an LLM is added, put it behind a narrow adapter with structured output validation. The deterministic policy layer should still be able to block unsafe requests even if the LLM suggests otherwise.

## Product Rule

LLM output must be treated as untrusted. It should not invent numbers, bypass policy, or replace deterministic financial decisions.

## Related Notes

- [[Assistant Response Policy]]
- [[Prompt Injection Rules]]
- [[Do Not Build Yet]]
