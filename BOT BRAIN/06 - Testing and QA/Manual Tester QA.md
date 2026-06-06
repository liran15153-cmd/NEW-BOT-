---
type: checklist
status: current
source: docs
---

# Manual Tester QA

The local tester lives at `/tester` and calls the real `/chat/message` endpoint.

## Use It To Check

- Hebrew answer quality
- scenario button behavior
- debug metadata
- missing-field flows
- transcript export
- local-only file preview
- new-session behavior

## How To Judge Manual Results

Do not only check that a response appears. Check whether the answer feels like the product should feel: short, practical, non-judgmental, and honest about demo data. Debug metadata should match the visible behavior. If the bot asks for missing data, `tool_executed` should be false. If the bot answers a completed financial question, reason codes should be present.

## Core Scenarios

- cashflow question
- purchase with amount
- purchase without amount followed by amount
- installment without amount/months followed by complete data
- new-topic override
- privacy question with purchase words
- unsupported loan or investment request
- unknown message

## Manual QA Red Flags

- answer text looks broken or has mojibake
- privacy questions trigger purchase tools
- unsupported advice sounds like a recommendation
- installment answers imply installments are automatically better
- future-feature requests claim to analyze transaction history
- a new session continues old state

## Related Notes

- [[Debug Metadata]]
- [[Current Product Behavior]]
- [[Acceptance Checklist]]
