---
type: concept
status: current
source: code
---

# Decision Engine

`financial_decision_engine.py` converts structured financial facts into structured outcomes.

## Outputs

- risk level
- reason codes
- recommended action
- computed amounts
- booleans such as `can_purchase`

## How To Think About Decisions

The decision engine should answer: "Given the facts, what is the structured financial interpretation?" It should not answer: "How should we phrase this to the user?" That wording belongs later.

For purchases, the core question is whether the user remains above or below a safe buffer after the purchase. For installments, the key value is the monthly payment impact. When an amount does not divide evenly across installments, the monthly payment should be rounded up to the nearest minor currency unit so the assistant does not understate the user's future obligation. For cashflow, the important context is available buffer, safe-to-spend amount, days until salary, and expected expenses. For weekly safe-spend, the key value is a conservative cap for the next 7 days, prorated from the safe-to-spend amount until salary and rounded down in minor units. For overdraft risk, the key value is projected balance before salary. A positive projection can still be medium risk when expected expenses are high; a negative projection must expose an overdraft gap and high risk.

## Risk Levels

- `low`
- `medium`
- `high`

## Recommended Actions

- `proceed`
- `wait`
- `reduce_amount`
- `avoid`
- `limit_to_safe_amount`
- `reduce_spending`

## Boundary

The decision engine must not contain user-facing Hebrew or English answer copy.

## Test Expectations

Tests should assert reason codes and recommended actions, not just one final string. If a future developer changes a threshold, tests should make the behavioral change visible.

## Related Notes

- [[Financial Contracts]]
- [[Demo Financial Context]]
- [[Data Readiness]]
