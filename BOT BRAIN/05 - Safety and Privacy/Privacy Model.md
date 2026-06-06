---
type: concept
status: current
source: docs
---

# Privacy Model

Privacy is a product requirement, not a later polish step.

## Current State

The system has no real user financial data, employer layer, database, or persistent storage. The current demo backend should not imply otherwise.

## Product Trust Rule

Privacy answers must be direct. If a user asks whether an employer can see their data, the bot should not dodge. It should state the current reality and the intended future boundary: personal balances, transactions, salaries, debts, and questions should not be employer-visible.

## Employer Boundary

Future employer analytics, if built, must be aggregated and anonymized. Employers should not see balances, transactions, salaries, debts, or personal financial questions.

## Current Privacy Answer

Privacy questions are allowed and should explain that no employer-facing layer or real financial data exists in the current system.

## Future Risk

Employer analytics are dangerous if designed too early. Even aggregated analytics need explicit anonymization rules, minimum cohort sizes, retention policy, consent text, and deletion/export flows.

## Related Notes

- [[Assistant Response Policy]]
- [[Do Not Build Yet]]
- [[Open Decisions]]
