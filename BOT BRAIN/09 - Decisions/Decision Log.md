---
type: decision
status: current
source: docs
---

# Decision Log

## Current Decisions

- Build the bot brain before production infrastructure.
- Keep the backend deterministic and local for now.
- Use FastAPI for the backend.
- Keep routes thin.
- Keep financial facts separate from answer wording.
- Keep final Hebrew copy centralized in `hebrew_response_builder.py`.
- Support weekly safe-spend as a deterministic projection before richer data infrastructure.
- Support overdraft risk before salary as a deterministic projection from demo cash-flow facts.
- Support upcoming-expense pressure as deterministic demo commitments without merchant names.
- Use in-memory state only for short clarification flows.
- Recognize unsupported and future intents without pretending they are implemented.
- Keep tests as architecture guardrails.

## Decision Details

Bot brain first: The team needs to prove useful conversation behavior before adding sensitive infrastructure. This is why WhatsApp, Supabase, Open Banking, and LLMs remain deferred.

Deterministic first: The current system uses rules and structured tools so behavior can be tested directly. This reduces the chance of fake financial certainty.

Weekly safe-spend: This is a useful employee question that can be answered from
the existing demo cash-flow facts. It should stay conservative: prorate the
safe-to-spend amount until salary across the next 7 days and round down in minor
currency units.

Overdraft risk before salary: This is a core employee question and can be
answered honestly from existing demo facts without new infrastructure. The
decision separates "no projected overdraft" from "low risk" so expected expense
pressure can still produce a cautious answer.

Upcoming expense pressure: This answers a concrete "what is coming soon?"
question without pretending to analyze transaction history. The current contract
uses generic committed totals and timing, not merchant names or subscriptions.

Centralized Hebrew copy: The product is Hebrew-facing, so answer quality needs one obvious ownership point. Scattered copy would make QA and tone control harder.

In-memory dialogue only: Short clarification is useful, but long-term memory would create privacy and data-retention obligations too early.

## Rationale

The project is still proving whether the conversation core is useful. Premature infrastructure would increase complexity without improving the actual user experience.

## Related Notes

- [[Architecture Principles]]
- [[Do Not Build Yet]]
- [[Open Decisions]]
