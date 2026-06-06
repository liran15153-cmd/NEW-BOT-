---
type: concept
status: current
source: code
---

# Parameter Extractor

`financial_parameter_extractor.py` extracts structured parameters from user text.

## Current Parameters

- `amount_minor`
- `currency`
- `months`

## Why Minor Units Matter

Financial code should avoid floating-point errors. Representing `400 shekels` as `40000` keeps calculations deterministic and testable. Formatting back to `₪` belongs at the response boundary, not inside the decision engine.

## Supported Money Formats

- `400 שקל`
- `400 ש"ח`
- `400 שח`
- `400 ₪`
- `₪400`
- `1,200 שקל`
- `1200 שקל`
- `400 nis`
- `400 shekels`

## Invalid Values

Negative amounts, zero amounts, malformed amounts, and zero installment months should not execute tools. They should produce controlled missing-field behavior.

## Common Failure Modes

- Treating installment count as an amount.
- Treating `-400 shekels` as `400 shekels`.
- Accepting malformed comma placement.
- Missing Hebrew maqaf variants such as `ל־3 תשלומים`.

Every new parsing rule should come with tests.

## Related Notes

- [[Money Representation]]
- [[Financial Intent Parser]]
- [[Testing Map]]
