---
type: map
status: current
source: tests
---

# Testing Map

The test suite is part of the architecture. It proves not only happy paths, but also product safety, policy behavior, and module boundaries.

## Current Baseline

`103 passed` is the current known-good baseline.

## Coverage Areas

- [[Test Suite Overview]] for categories and files.
- [[Manual Tester QA]] for browser-based scenario testing.
- [[Acceptance Checklist]] for definition of done.
- [[Safety Boundaries]] for blocked advice behavior.
- [[Assistant Response Policy]] for policy-level decisions.
- [[Data Readiness]] for uncertainty and missing-data behavior.

## Why Tests Matter Here

This project has several subtle failure modes that are easy to miss manually. A loan question can look like a purchase question. A missing amount can accidentally execute a tool. A privacy question can contain purchase words. A future-feature request can tempt the bot to pretend it has transaction history. Tests protect against those errors.

The test suite is also documentation. When behavior is unclear, read the test that asserts it. If code and prose disagree, passing tests and current code should be treated as the first source of truth until the docs are corrected.

## When To Add Tests

Add tests whenever you change parsing keywords, response policy, missing-field behavior, financial decision thresholds, answer copy boundaries, or debug metadata. Do not wait until the end of a feature.

## What Tests Must Keep Proving

- incomplete requests do not execute tools
- unsupported advice stays blocked
- privacy questions do not execute purchase tools
- future feature requests ask for transaction history
- Hebrew answer text remains centralized
- no deferred integration packages are introduced by accident

## Related Notes

- [[System Map]]
- [[Architecture Principles]]
- [[Do Not Build Yet]]
