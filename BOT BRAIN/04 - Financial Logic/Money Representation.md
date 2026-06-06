---
type: concept
status: current
source: code
---

# Money Representation

Money is represented in minor units.

## Current Currency

`ILS` is the only current supported currency.

## Example

`400 shekels` -> `40000`

## Why This Matters

Money should not be represented with floats in core logic because rounding errors are unacceptable in financial decisions. Minor units make comparisons simple: `amount_minor > safe_to_spend_minor` is deterministic and easy to test.

## Display Boundary

Formatting money as `₪` belongs in final response code. Core contracts and decisions should keep numeric values structured.

## Rules

- Do not use floating-point arithmetic for core money calculations.
- Reject or ignore invalid amounts before tool execution.
- Keep display formatting in response code, not decision logic.

## Related Notes

- [[Parameter Extractor]]
- [[Financial Contracts]]
- [[Decision Engine]]
