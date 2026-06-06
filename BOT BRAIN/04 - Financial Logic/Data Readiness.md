---
type: concept
status: current
source: code
---

# Data Readiness

`financial_context_readiness.py` evaluates whether the available financial context is strong enough to answer a question.

## Levels

- `none`: no usable financial data
- `low`: partial data exists, but not enough for core decisions
- `medium`: useful estimate may be possible, but uncertainty is required
- `high`: stronger context exists, but projections still need uncertainty

## Why Readiness Exists

The assistant should not treat all data as equally reliable. A transaction list without current balance is different from a live account snapshot. A stale import is different from fresh data. Readiness gives the policy layer a structured way to decide whether to answer, ask for missing data, or include uncertainty.

## Intent-Specific Requirements

Projection-style intents need enough context to estimate near-term cash flow. Transaction-history intents need transactions. A system that knows the current balance but has no transactions still cannot detect subscriptions or money leaks.

## Missing Fields

Projection intents may require current balance and salary date. Transaction-history intents require transactions.

## Uncertainty Triggers

- no or partial data
- possible duplicates
- import warnings
- projection-style answers

## Product Implication

When readiness is weak, the bot should be honest. It can still help, but it should avoid acting as if the estimate is guaranteed.

## Related Notes

- [[Assistant Response Policy]]
- [[Future Data Sources]]
- [[User Experience Principles]]
