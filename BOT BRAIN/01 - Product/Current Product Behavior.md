---
type: concept
status: current
source: docs
---

# Current Product Behavior

The backend supports a narrow but valuable set of financial wellness conversations using demo facts.

## Supported Behavior

- `cashflow_status`: answer how much buffer remains until salary day.
- `weekly_spend`: estimate what can safely be spent this week from demo facts.
- `simulate_purchase`: check whether a specific purchase fits the demo buffer.
- `simulate_installments`: estimate monthly payment impact for installments.
- `privacy_question`: explain current and future privacy boundaries.
- unsupported investment, loan, tax, and legal advice: respond safely without tool execution.
- future transaction-history features: ask for missing transaction data.

## Behavior By Scenario

Cash-flow questions should explain available buffer, safe-to-spend amount, days until salary, and risk level when those values exist. Weekly safe-spend questions should give a conservative cap for the next 7 days, calculated from the safe-to-spend amount until salary and rounded down in minor units. Purchase questions should never answer only "yes" or "no"; they should explain whether the purchase is safe, tight, or not recommended. Installment questions should mention monthly payment impact and avoid presenting installments as automatically better.

Privacy questions should answer the user's concern directly. The current system has no employer-facing layer and no real user financial data. Future employer analytics, if ever built, must be aggregated and anonymized.

Future-feature requests such as subscriptions, money leaks, or transaction explanations should ask for transaction history. They should not pretend to analyze data that is not available.

## Response Metadata

The response includes both product fields and debug fields. Product consumers should use `answer`, `intent`, `status`, `tool_called`, `confidence`, and `missing_fields`. Debug fields are for development and tests.

## Important Limits

All answers are based on demo context. The system must not imply that it checked a real bank account, employer system, live transaction feed, or real salary schedule.

## Related Notes

- [[Supported Intents]]
- [[Demo Financial Context]]
- [[Assistant Response Policy]]
