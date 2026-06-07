---
type: concept
status: current
source: code
---

# Demo Financial Context

The current backend uses deterministic demo financial facts. These are not live account data.

## Current Purpose

Demo context allows the bot-brain flow, decision engine, policy layer, and Hebrew responses to be tested without real bank data, imports, authentication, or persistence.

## What Demo Context Proves

Demo facts let the project verify the shape of decisions before real data exists. The team can test whether the system handles safe purchases, tight purchases, risky purchases, installments, and cash-flow explanations without exposing real users or building a database too early.

The default demo facts currently support weekly safe-spend projection too:
`500.00 ILS` safe-to-spend over 9 days until salary becomes `388.88 ILS` for
the next 7 days. The projection uses integer minor-unit math and rounds down.

They also support overdraft-risk projection before salary:
`2500.00 ILS` current balance minus `1800.00 ILS` committed expenses leaves
`700.00 ILS` projected before salary. That means no overdraft is currently
projected, but expected expenses are still high, so the decision remains medium
risk.

They also support upcoming-expense pressure:
`650.00 ILS` in committed expenses across 3 generic charges is expected in the
next 7 days. The largest upcoming expense is `450.00 ILS`, the next charge is in
2 days, and the projected balance after near-term commitments is `1850.00 ILS`.
These are generic demo commitments, not merchant-level transaction history.

Demo context is not a toy if it is used correctly. It is the contract rehearsal for production data.

## Product Wording Rule

Answers should say they are based on demo data. They must not claim that the bot checked a real bank account or live salary schedule.

## Future Replacement

The demo context can later be replaced by manual input, CSV import, database-backed demo data, or Open Banking, but that decision is still open.

## Replacement Rule

When a real source replaces demo facts, it should feed the same kind of structured facts into the decision engine. Do not let the data source dictate user-facing language or bypass safety policy.

## Related Notes

- [[Financial Contracts]]
- [[Future Data Sources]]
- [[Data Readiness]]
