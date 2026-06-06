---
type: checklist
status: current
source: docs
---

# How To Work On This Project

Future agents should inspect before changing. Do not invent architecture or assume future integrations exist.

## Rules

- Read relevant files first.
- Keep changes small and focused.
- Preserve module boundaries.
- Do not add dependencies unless justified.
- Do not add deferred integrations by accident.
- Add or update tests for behavior changes.
- Update docs and vault notes when behavior changes.
- Run tests before claiming completion.

## Recommended Work Sequence

1. Inspect the relevant code and tests.
2. Identify the owning layer.
3. Write or update tests for the behavior.
4. Make the smallest code change.
5. Run the relevant test subset, then the full suite when appropriate.
6. Update docs and vault notes if behavior or architecture changed.
7. Report what changed and what remains risky.

## Critical Review Standard

Do not agree with infrastructure expansion by default. If a request jumps to WhatsApp, Supabase, Open Banking, a dashboard, or an LLM before the bot-brain need is proven, challenge it and propose the smaller product-learning step.

## Critical Product Bias

Improve the bot brain and user experience before infrastructure. If a requested direction is premature, say why and suggest the simpler path.

## Related Notes

- [[Change Checklist]]
- [[Acceptance Checklist]]
- [[Do Not Build Yet]]
