---
type: concept
status: current
source: code
---

# Financial Intent Parser

`financial_intent_parser.py` detects executable financial intents used by the current deterministic tool path.

## Current Executable Intents

- `cashflow_status`
- `simulate_purchase`
- `simulate_installments`
- `unknown`

## Difference From Assistant Intent

This parser exists for the current tool path. It is narrower than [[Assistant Intent Classifier]] and should not decide unsupported advice, privacy, or future feature policy. Those concerns belong to the assistant-level classifier and response policy.

## Keyword Quality

Keyword rules should be practical rather than clever. Add examples from real tester messages. If a keyword creates ambiguity, add tests for both the intended match and a near-miss that should not match.

## Design Rule

The parser should stay simple, deterministic, and testable. It should not become an LLM wrapper or a hidden policy layer.

## Interaction With Assistant Intent

Assistant-level intent classification can override execution when the message is privacy-related, unsafe, or unsupported. This prevents dangerous routing.

## Related Notes

- [[Assistant Intent Classifier]]
- [[Parameter Extractor]]
- [[Supported Intents]]
