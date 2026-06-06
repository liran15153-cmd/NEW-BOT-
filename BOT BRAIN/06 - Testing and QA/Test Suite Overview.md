---
type: concept
status: current
source: tests
---

# Test Suite Overview

The current baseline is `103 passed`.

## What The Suite Covers

- health endpoint
- chat message API
- assistant intent classification
- assistant policy schemas
- assistant response policy
- answer plan
- policy integration
- financial context readiness
- financial intent and parameter parsing
- financial contracts
- financial decision engine
- conversation state
- multi-turn conversation flows
- local tester app
- architecture boundaries
- system audit checks

## How To Read The Tests

The tests are organized around behavior, not just modules. API tests prove response contracts. Policy tests prove safety decisions. Integration tests prove that policy wins over misleading purchase keywords. Architecture tests prevent Hebrew copy and user-facing behavior from drifting into the wrong modules.

## Most Important Regression Risks

- unsafe advice accidentally executes a tool
- missing data accidentally executes a tool
- future transaction-history features pretend to work
- Hebrew response copy moves out of the response builder
- deferred dependencies appear in `pyproject.toml`
- conversation state leaks across sessions

## Rule

Every behavior change should add or update tests. The suite must stay local and deterministic.

## Related Notes

- [[Testing Map]]
- [[Acceptance Checklist]]
- [[Manual Tester QA]]
