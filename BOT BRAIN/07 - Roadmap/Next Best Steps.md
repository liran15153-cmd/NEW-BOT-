---
type: roadmap
status: current
source: docs
---

# Next Best Steps

The next useful work is still bot-brain quality, not infrastructure.

## Recommended Path

1. Keep tests green.
2. Run manual QA through `/tester`.
3. Improve deterministic intent and parameter coverage.
4. Add richer demo financial scenarios.
5. Strengthen uncertainty handling.
6. Decide the first real data source only after the bot-brain contract feels stable.

## What "Stable Bot Brain" Means

The bot brain is stable when the supported scenarios work repeatedly in `/tester`, Hebrew answers feel natural, unsupported requests are blocked without sounding useless, missing-data flows are smooth, and tests protect all important branches.

## Suggested Next Product Scenario

Weekly safe-spend, overdraft risk before salary, and upcoming-expense pressure
are now current deterministic scenarios. The next useful step is no longer
another demo-only projection; it should either restore the full dev/test/push
environment or choose the first real data path, such as manual transaction input
or CSV import. If real transaction or import work starts, recurring-payment
detection becomes a better next subsystem.

## Not Next

Do not jump to WhatsApp, Supabase, Open Banking, auth, dashboard, or real LLM before the conversation core is strong.

## Related Notes

- [[Do Not Build Yet]]
- [[Future Data Sources]]
- [[Manual Tester QA]]
