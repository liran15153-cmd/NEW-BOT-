---
type: decision
status: current
source: docs
---

# Open Decisions

These should not be guessed by future agents.

## Product And Data

- What is the first real data source?
- What is the default safe-buffer threshold?
- How should safe, tight, and risky be defined in production?
- When should recurring-payment detection become active?
- What employer analytics are allowed, if any?

## How To Resolve These

Each open decision needs a small written proposal before implementation. The proposal should include user value, data required, privacy impact, test plan, and why now is the right time.

Do not resolve these implicitly by writing code. For example, adding a database schema effectively chooses a data model. Adding a WhatsApp webhook effectively chooses a channel. Those are product decisions, not just technical tasks.

## Privacy And Compliance

- What data retention policy is acceptable?
- What deletion and export behavior is required?
- What consent text is required before using real financial data?
- What compliance requirements apply before launch?

## Integrations

- When should WhatsApp become the first real channel?
- When is a real LLM useful enough to justify privacy and reliability risk?

## Highest-Risk Open Decisions

The riskiest unresolved areas are real financial data, employer analytics, and LLM use. These can change the trust model of the product and should not be handled as routine engineering tasks.

## Related Notes

- [[Future Data Sources]]
- [[WhatsApp Stage]]
- [[Real LLM Stage]]
