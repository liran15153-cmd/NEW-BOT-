---
type: concept
status: current
source: code
---

# Financial Contracts

`financial_contracts.py` defines structured inputs, result models, currencies, risk levels, and tool protocols.

## Current Contract Shape

- `CashflowStatusInput` -> `CashflowStatusResult`
- `PurchaseSimulationInput` -> `PurchaseSimulationResult`
- `InstallmentsSimulationInput` -> `InstallmentsSimulationResult`

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
