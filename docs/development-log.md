# Development Log

## 2026-06-07 - Deterministic Overdraft Risk

- Added `overdraft_risk` as a supported deterministic bot-brain intent.
- Added structured overdraft-risk contracts, demo facts, decision output, reason codes, and Hebrew response text.
- The current rule projects balance before salary as current balance minus committed expenses until salary.
- A negative projection returns an overdraft gap and high risk.
- A positive projection can still be medium risk when expected expenses are high, so the answer does not collapse into a naive yes/no.
- This remains demo-data behavior only; it does not access live bank data, salary data, employer systems, or transaction feeds.
