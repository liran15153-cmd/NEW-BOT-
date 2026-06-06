---
type: concept
status: current
source: docs
---

# Unsupported Behaviors

Unsupported behavior should be recognized safely, not ignored or faked.

## Unsupported Advice

- investment recommendations
- stock, crypto, fund, or securities advice
- loan recommendations
- tax advice
- legal advice

These produce useful safe responses but do not execute financial tools.

## How Unsupported Should Feel

Unsupported does not mean useless. The assistant should clearly say what it cannot do, then offer a safe adjacent action when one exists. For example, it cannot recommend taking a loan, but it can help estimate how a specific monthly payment would affect cash flow once the user provides the amount and terms.

The tone should be firm but not bureaucratic. The user should understand the boundary without feeling scolded.

## Future Features Not Active Yet

- recurring expense detection
- subscription detection
- money leak analysis
- transaction explanation
- CSV upload
- Open Banking
- WhatsApp
- real LLM explanations
- employer analytics

## Product Rule

Recognizing a future intent is not permission to implement it. Future features need their own plan, tests, privacy review, and architecture boundary.

## Risk Of Faking Future Behavior

The most damaging mistake would be pretending to detect subscriptions, leaks, or transaction explanations without transaction history. That creates fake trust. The current safer behavior is to say transaction history is required.

## Related Notes

- [[Safety Boundaries]]
- [[Do Not Build Yet]]
- [[Open Decisions]]
