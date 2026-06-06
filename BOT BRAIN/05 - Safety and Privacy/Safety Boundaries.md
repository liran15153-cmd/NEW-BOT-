---
type: concept
status: current
source: docs
---

# Safety Boundaries

The assistant must be useful without becoming an advisor in unsupported areas.

## Blocked Advice

- investment recommendations
- stocks, crypto, funds, or securities advice
- loan recommendations
- tax advice
- legal advice

## Why These Are Blocked

These categories carry legal, financial, or compliance risk. The current product is a cash-flow helper, not a licensed financial advisor, lender, lawyer, tax advisor, or broker. Blocking these requests keeps the product honest and focused.

## Safe Redirect Pattern

When possible, redirect from the unsupported request to a supported cash-flow question. For example, instead of recommending a loan, the bot can say it cannot recommend taking a loan but can help estimate how a monthly payment would affect the user's cash flow.

## Allowed Alternative

The bot may redirect to cash-flow impact analysis when appropriate, but it must not recommend a financial product or legal/tax action.

## Tool Execution Rule

Unsupported advice responses do not execute financial tools.

## Test Signal

Policy integration tests should prove that unsupported requests with purchase words still do not execute purchase tools.

## Related Notes

- [[Assistant Response Policy]]
- [[Unsupported Behaviors]]
- [[Prompt Injection Rules]]
