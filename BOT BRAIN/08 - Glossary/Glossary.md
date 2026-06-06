---
type: concept
status: current
source: code
---

# Glossary

## Terms

- `intent`: executable financial intent used by the current tool path.
- `assistant_intent`: policy-level intent used to classify safety and future-feature requests.
- `response_type`: policy output such as `cautious_estimate` or `unsupported_request`.
- `readiness`: how complete the available financial context is.
- `reason_code`: structured explanation for a financial decision.
- `safe_to_spend_minor`: demo safe-to-spend amount in minor units.
- `amount_minor`: money amount represented in minor units.
- `tool_executed`: debug flag proving whether a financial tool ran.
- `state_continued`: debug flag showing a pending dialogue state was continued.
- `unsupported_request`: safe response type for blocked advice areas.

## Extended Definitions

`intent` is the narrow financial route used by current tools. It should answer whether the system can execute `cashflow_status`, `simulate_purchase`, or `simulate_installments`.

`assistant_intent` is broader. It captures safety and product categories such as privacy questions, unsupported loan advice, and recurring expense requests.

`response_type` is the policy decision about the shape of the response. It helps separate "what kind of answer is safe?" from "what exact Hebrew sentence should we write?"

`readiness` describes whether the available financial context is strong enough. A high readiness level still does not mean the future is guaranteed.

`reason_code` is a structured explanation for a financial decision. It is better than free text because tests can assert it and the response builder can translate it into user-facing language.

`safe_to_spend_minor` is not a universal financial truth. It is a demo threshold used to prove decision behavior.

## Maintenance Rule

Whenever a new enum, policy type, reason code, or financial term is added, update this glossary. Otherwise future agents will guess.

## Related Notes

- [[Supported Intents]]
- [[Data Readiness]]
- [[Decision Engine]]
