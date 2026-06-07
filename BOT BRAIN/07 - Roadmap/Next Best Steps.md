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

Weekly safe-spend and overdraft risk before salary are now current deterministic
scenarios. The next useful cash-flow scenario is likely upcoming-expense
pressure, still using demo facts and deterministic services. If real transaction
or import work starts, recurring-payment detection becomes a better next
subsystem than another demo-only projection.

## Not Next

Do not jump to WhatsApp, Supabase, Open Banking, auth, dashboard, or real LLM before the conversation core is strong.

## Related Notes

- [[Do Not Build Yet]]
- [[Future Data Sources]]
- [[Manual Tester QA]]
