---
type: checklist
status: current
source: docs
---

# Acceptance Checklist

Use this before claiming a change is complete.

## Required Checks

- relevant code path works locally
- relevant tests pass
- no sensitive data is logged
- financial calculations remain deterministic
- user-facing Hebrew copy remains centralized
- incomplete requests do not execute tools
- unsupported advice does not execute tools
- docs or vault notes are updated when behavior changes
- remaining risks are stated clearly

## Strong Definition Of Done

A change is not done just because tests pass. For conversation behavior, the local tester should also be checked. For architecture changes, module ownership should still make sense. For product behavior changes, the vault and docs should still match the actual system.

## Reporting Standard

When finishing work, report what changed, what tests ran, what was not tested, and what risk remains. Do not claim production readiness for a local deterministic demo backend.

## Command

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Related Notes

- [[Test Suite Overview]]
- [[How To Work On This Project]]
- [[Change Checklist]]
