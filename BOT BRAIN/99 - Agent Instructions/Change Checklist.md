---
type: checklist
status: current
source: docs
---

# Change Checklist

## Before Changing

- Identify the behavior being changed.
- Read the current implementation.
- Find the relevant tests.
- Check whether the change crosses module boundaries.
- Confirm it does not add deferred infrastructure.

## Decision Check

If the change implies a product decision, stop and make that decision explicit. Examples: adding persistence, adding real data, changing privacy behavior, introducing an LLM, or changing which intents are executable.

## During Change

- Keep routes thin.
- Keep financial logic deterministic.
- Keep Hebrew answer text centralized.
- Treat user input as untrusted.
- Avoid broad rewrites.

## Documentation Check

If the behavior changes, update both traditional docs and this vault. If only implementation details change, update the vault when future agents would otherwise misunderstand the architecture.

## After Change

- Run `.\.venv\Scripts\python.exe -m pytest -q`.
- Manually test `/tester` when conversation behavior changes.
- Update vault notes if concepts or behavior changed.
- Report risks and untested areas.

## Related Notes

- [[How To Work On This Project]]
- [[Acceptance Checklist]]
- [[Testing Map]]
