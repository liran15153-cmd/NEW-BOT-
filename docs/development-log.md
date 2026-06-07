# Development Log

## 2026-06-07 - Deterministic Upcoming Expense Pressure

- Added `upcoming_expenses` as a supported deterministic bot-brain intent.
- Added structured upcoming-expense contracts, demo facts, decision output, reason codes, and Hebrew response text.
- The current rule projects near-term balance as current balance minus committed expenses in the next 7 days.
- The answer includes total upcoming amount, number of charges, next due timing, largest upcoming expense, and projected balance after near-term commitments.
- The flow does not invent merchant names, subscription names, live transactions, or bank data.

## 2026-06-07 - Deterministic Overdraft Risk

- Added `overdraft_risk` as a supported deterministic bot-brain intent.
- Added structured overdraft-risk contracts, demo facts, decision output, reason codes, and Hebrew response text.
- The current rule projects balance before salary as current balance minus committed expenses until salary.
- A negative projection returns an overdraft gap and high risk.
- A positive projection can still be medium risk when expected expenses are high, so the answer does not collapse into a naive yes/no.
- This remains demo-data behavior only; it does not access live bank data, salary data, employer systems, or transaction feeds.
