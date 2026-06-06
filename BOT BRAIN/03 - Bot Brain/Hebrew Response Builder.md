---
type: concept
status: current
source: code
---

# Hebrew Response Builder

`hebrew_response_builder.py` owns all final user-facing Hebrew answer text.

## Why It Matters

Centralizing Hebrew copy prevents scattered product behavior, makes tone easier to review, and keeps financial modules from becoming presentation code.

## Responsibilities

- build answered responses
- build missing-info responses
- build unknown responses
- build policy responses
- phrase demo-data limitations clearly
- avoid fake certainty
- avoid unsupported financial advice

## What Makes A Good Hebrew Answer

Good Hebrew copy should be short, natural, and practical. It should not sound like a literal translation from English. It should say when the answer is based on demo data, avoid judgmental phrasing, and clearly ask for missing information when needed.

## Review Checklist

- Does it mention demo data when relevant?
- Does it avoid saying the bot checked real bank data?
- Does it avoid unsupported advice?
- Does it explain the practical consequence?
- Is the Hebrew readable in the local tester?

## Forbidden Drift

Do not move final user-facing Hebrew copy into routes, financial tools, decision engine, policy, planner, or dialogue code.

## Related Notes

- [[User Experience Principles]]
- [[Answer Plan]]
- [[Architecture Principles]]
