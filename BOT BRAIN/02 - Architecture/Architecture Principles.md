---
type: concept
status: current
source: docs
---

# Architecture Principles

The current architecture is intentionally small and deterministic.

## Rules

- API routes stay thin.
- Business logic lives in services and bot-brain modules.
- Financial tools return structured facts only.
- The decision engine returns structured outcomes only.
- User-facing Hebrew text belongs in [[Hebrew Response Builder]].
- Conversation state is short-lived and replaceable.
- Debug metadata is for internal testing, not product behavior.
- Tests define the architecture guardrails.

## Why These Rules Exist

The product handles financial questions, so mistakes are more costly than in a normal chatbot. A casual architecture can create answers that sound confident but are based on incomplete data. These rules force every answer to pass through explicit layers: classification, parameter extraction, data readiness, deterministic tools, decisions, and final wording.

The most important separation is between "facts" and "phrasing". Financial modules should know numbers and risk. The response builder should know how to explain them. Mixing those makes it hard to audit whether the bot invented something.

## Practical Review Questions

Before accepting a change, ask:

- Did this add a new hidden source of truth?
- Did this move user-facing text out of the response builder?
- Did this make the router more than an orchestrator?
- Did this create long-term memory by accident?
- Did this add infrastructure before the bot-brain contract needed it?

## Deferred Architecture

Do not add database models, Supabase, WhatsApp, Open Banking, auth, dashboard, background jobs, or LLM adapters until the bot-brain contract is stable.

## Related Notes

- [[Code Ownership Map]]
- [[Request Response Flow]]
- [[Do Not Build Yet]]
