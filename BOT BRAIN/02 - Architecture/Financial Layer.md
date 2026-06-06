---
type: system
status: current
source: code
---

# Financial Layer

The financial layer owns structured financial facts and deterministic decisions.

## Current Modules

- `financial_contracts.py`: input/result models and protocols
- `demo_financial_tools.py`: deterministic demo context
- `financial_decision_engine.py`: risk and recommendation decisions
- `financial_reason_codes.py`: structured reason codes

## Core Rule

Financial modules do not write user-facing copy. They produce facts, decision results, risk levels, recommended actions, and reason codes.

## Why Structured Facts Matter

Financial decisions need to be auditable. If a tool returns a sentence like "this purchase is safe", the system loses visibility into why. If it returns `buffer_after_purchase_minor`, `safe_to_spend_minor`, and `days_until_salary`, the decision engine can make a clear, testable decision and the response builder can explain it.

## Current Limitation

The current facts are demo facts only. They are useful for proving behavior, but they are not real user context. Any future replacement must preserve the same structured contract or deliberately migrate it with tests.

## Related Notes

- [[Financial Contracts]]
- [[Demo Financial Context]]
- [[Decision Engine]]
- [[Money Representation]]
