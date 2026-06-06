---
type: roadmap
status: future
source: docs
---

# Future Data Sources

The first real data source is still an open decision.

## Options

- manual entry
- CSV import
- database-backed demo data
- Open Banking

## Option Notes

Manual entry is fastest for testing user experience but least scalable. CSV import proves deterministic ingestion and can work before bank integrations. Database-backed demo data helps create repeatable scenarios. Open Banking is closest to real value but has the highest privacy, compliance, and reliability burden.

## Tradeoff

Manual or database-backed demo data may be safer before external integrations. CSV import can prove deterministic ingestion. Open Banking has the highest privacy and compliance burden.

## Required Before Implementation

- privacy rules
- retention policy
- deletion/export behavior
- data validation
- tests
- clear product scope

## Recommended Bias

Prefer the smallest data source that lets the team test real product behavior. Do not choose Open Banking just because it sounds complete.

## Related Notes

- [[Data Readiness]]
- [[Open Decisions]]
- [[Do Not Build Yet]]
