---
type: concept
status: current
source: code
---

# Supported Intents

There are two related intent layers: assistant-level intents and executable financial intents.

## Assistant Intents

- `cashflow_status`
- `weekly_safe_spend`
- `overdraft_risk`
- `upcoming_expenses`
- `affordability_check`
- `payment_split_simulation`
- `recurring_expenses`
- `money_leak_detection`
- `transaction_explanation`
- `privacy_question`
- `unsupported_investment_advice`
- `unsupported_loan_advice`
- `unsupported_tax_or_legal_advice`
- `general_help`
- `unknown`

## Why Two Intent Layers Exist

The assistant-level intent layer protects product policy. It sees categories like privacy questions, unsupported investment advice, and future transaction-history requests. The executable financial intent layer is narrower and maps only to current deterministic tools.

This split is important because one user message can contain overlapping signals. "Should I take a loan to buy this?" contains purchase language, but the correct product behavior is not a purchase simulation. It is unsupported loan advice.

## Executable Current Tools

- `cashflow_status` -> `cashflow_status`
- `weekly_safe_spend` -> `weekly_spend`
- `overdraft_risk` -> `overdraft_risk`
- `upcoming_expenses` -> `upcoming_expenses`
- `affordability_check` -> `simulate_purchase`
- `payment_split_simulation` -> `simulate_installments`

## Recognized But Not Executed

- `recurring_expenses`
- `money_leak_detection`
- `transaction_explanation`

These require transaction history and must not pretend to work without it.

## Implementation Rule

Adding a new assistant intent is not enough. A complete intent change needs classifier rules, policy behavior, response copy, debug expectations, tests, and documentation. If the intent executes a tool, it also needs contracts and decision logic.

## Related Notes

- [[Assistant Intent Classifier]]
- [[Financial Intent Parser]]
- [[Assistant Response Policy]]
