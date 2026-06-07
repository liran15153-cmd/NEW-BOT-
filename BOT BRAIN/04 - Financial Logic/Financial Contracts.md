---
type: concept
status: current
source: code
---

# Financial Contracts

`financial_contracts.py` defines structured inputs, result models, currencies, risk levels, and tool protocols.

## Current Contract Shape

- `CashflowStatusInput` -> `CashflowStatusResult`
- `WeeklySpendInput` -> `WeeklySpendResult`
- `OverdraftRiskInput` -> `OverdraftRiskResult`
- `PurchaseSimulationInput` -> `PurchaseSimulationResult`
- `InstallmentsSimulationInput` -> `InstallmentsSimulationResult`

`WeeklySpendResult` carries the safe-to-spend amount until salary, daily
safe-to-spend amount, projected weekly safe-to-spend amount, projection days,
remaining days until salary, and projected buffer after that weekly spend. These
are facts for the response builder; they are not user-facing prose.

`OverdraftRiskResult` carries current balance, committed expenses until salary,
projected balance before salary, overdraft gap, days until salary, currency, and
expected-expense pressure. It is still a deterministic projection from available
facts, not a final answer string.

## Design Rule

Contracts carry facts, not prose. They should stay stable because multiple layers depend on them: tool executor, decision engine, response builder, and tests.

## Why Contracts Are Core Infrastructure

The contracts are the seam between "available data" and "assistant behavior". They define what the bot is allowed to know. If contracts are vague, the response builder can start relying on hidden assumptions. If contracts are structured, tests can verify every value used in an answer.

## Change Guidance

Changing a contract should be treated as a serious change. Update financial tools, decision engine, response builder, tests, docs, and vault notes together. Do not add optional fields that no one understands just because they might be useful later.

## Related Notes

- [[Financial Layer]]
- [[Decision Engine]]
- [[Money Representation]]
