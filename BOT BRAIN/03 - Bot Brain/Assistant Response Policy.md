---
type: concept
status: current
source: code
---

# Assistant Response Policy

`assistant_response_policy.py` decides whether a response is allowed, blocked, uncertain, missing-data-driven, or privacy-focused before the final answer is written.

## Response Types

- `direct_answer`
- `cautious_estimate`
- `ask_for_missing_data`
- `clarifying_question`
- `unsupported_request`
- `privacy_explanation`
- `error_fallback`

## Safety Decisions

Investment, loan, tax, and legal advice are blocked as unsupported requests. Privacy questions are allowed as privacy explanations. Future transaction-history features ask for missing data instead of pretending to work.

## Policy Inputs

The policy receives the user message, assistant intent, optional financial context summary, calculation result, and missing fields. It decides response type and safety metadata; it does not generate final answer copy.

## Policy Outputs

The policy returns whether the response is allowed, which response type to use, why a request was blocked or uncertain, what fields are missing, which disclaimers are required, and whether uncertainty must be included.

## Uncertainty

Projection-style financial answers normally require uncertainty, even when context is strong. Future cash flow is never guaranteed.

## Design Rule

Policy should be explicit and structured. Do not hide safety behavior in free-text answers. Tests should be able to assert the policy decision directly.

## Related Notes

- [[Answer Plan]]
- [[Data Readiness]]
- [[Safety Boundaries]]
