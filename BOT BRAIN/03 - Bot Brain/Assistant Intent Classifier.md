---
type: concept
status: current
source: code
---

# Assistant Intent Classifier

`assistant_intent_classifier.py` classifies broad policy-level user intent before executable financial routing.

## Why It Exists

It prevents unsafe or unsupported requests from being misrouted as purchase, cash-flow, or installment checks. For example, a loan question that contains purchase words should still become `unsupported_loan_advice`.

## Classifier Categories

The classifier covers three kinds of user messages: executable current product requests, safety/policy requests, and future product requests. Executable requests can map to tools. Safety/policy requests return safe answers. Future requests are recognized but normally ask for missing transaction history or explain that the feature is not active yet.

## Precedence

Unsupported tax/legal, investment, and loan requests are checked before privacy, payment split, affordability, cashflow, and future transaction-history features.

## Executable Mapping

Only three assistant intents map to executable current tools:

- `cashflow_status`
- `affordability_check`
- `payment_split_simulation`

## Example

Message: `Should I take a loan to buy this for 1000 shekels?`

Expected assistant intent: `unsupported_loan_advice`

Reason: the loan boundary is more important than the purchase amount.

## Related Notes

- [[Supported Intents]]
- [[Assistant Response Policy]]
- [[Safety Boundaries]]
