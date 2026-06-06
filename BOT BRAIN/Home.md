---
type: map
status: current
source: docs
---

# BOT BRAIN

This vault is the second brain for the Financial Wellness Assistant backend. It explains what the product is, how the deterministic bot brain works, which boundaries are already enforced, and what must stay deferred until the core behavior is stable.

The current system is a local FastAPI backend for a Hebrew financial wellness bot. It supports `GET /health`, `POST /chat/message`, and a local browser tester at `/tester`. It does not yet include WhatsApp, Supabase, Open Banking, authentication, a database, a dashboard, real financial data, or a real LLM.

## Start Here

- [[System Map]] for the full request-to-response graph.
- [[Product Map]] for current product behavior and future capabilities.
- [[Code Ownership Map]] for module responsibilities.
- [[Testing Map]] for how the test suite protects behavior.
- [[Architecture Principles]] for the rules future changes must respect.
- [[Do Not Build Yet]] for explicitly deferred infrastructure.
- [[Next Best Steps]] for the recommended implementation path.

## Core Current Promise

The bot helps a user test simple near-term financial questions in Hebrew using deterministic demo facts:

- cash-flow status
- purchase affordability
- installment simulation
- privacy questions
- unsupported advice blocking
- future-feature requests that safely ask for missing data

## What This Vault Is For

Use this vault when you need to understand the project before changing it. The normal `docs/` folder explains the current implementation directly; this vault adds the "why", the relationships between concepts, the hidden risks, and the practical rules that should guide future development.

The most important idea is that this product is not ready for production infrastructure yet. The system is still proving the conversation core: can a user ask a short financial question, can the bot classify it safely, can it ask for missing data, can it avoid unsupported advice, and can it answer in clear Hebrew without inventing financial facts.

## How To Navigate

If you are making a code change, start with [[Code Ownership Map]], then read the subsystem note for the area you are touching. If you are changing product behavior, start with [[Current Product Behavior]], [[Supported Intents]], and [[User Experience Principles]]. If you are adding anything that sounds like a future integration, read [[Do Not Build Yet]] first.

If you are debugging a wrong bot answer, use this path:

1. [[Assistant Intent Classifier]]
2. [[Financial Intent Parser]]
3. [[Parameter Extractor]]
4. [[Dialogue Layer]]
5. [[Assistant Response Policy]]
6. [[Financial Decision Engine]]
7. [[Hebrew Response Builder]]

That order mirrors the runtime path and helps avoid fixing the wrong layer.

## Current Implementation Snapshot

The backend is a FastAPI app with dependency injection through `app.state`. The chat route creates a `ChatRouter` using app-level financial tools, conversation state store, and financial decision engine. The deterministic flow is tested locally with pytest and manually through the `/tester` browser surface.

The strongest parts today are the architecture boundaries, test coverage, and safety blocking. The weakest parts are still product depth and real financial data. That means the next valuable work is richer deterministic scenarios and better QA, not WhatsApp or Open Banking.

## Current Proof

The current verification baseline is `103 passed` with:

- API tests
- intent and parameter parsing tests
- dialogue state tests
- assistant policy tests
- financial decision tests
- architecture boundary tests
- system audit checks

## Related Notes

- [[Current Product Behavior]]
- [[Request Response Flow]]
- [[Assistant Response Policy]]
- [[Financial Decision Engine]]
- [[Acceptance Checklist]]
