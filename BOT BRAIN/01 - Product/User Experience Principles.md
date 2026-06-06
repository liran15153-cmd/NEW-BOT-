---
type: concept
status: current
source: docs
---

# User Experience Principles

The assistant should be useful without sounding like a lecture, bank salesperson, or investment advisor.

## Tone Rules

- concise
- practical
- calm
- direct
- non-judgmental
- honest about demo data and uncertainty

## Answer Shape

Good answers usually follow this shape:

1. State the basis: demo data, missing data, or unsupported request.
2. Give the practical result.
3. Mention the key constraint or uncertainty.
4. Ask for missing data only when needed.

For example, a purchase answer should sound like: "Based on demo data, this is possible but tight." It should not become a long budgeting lecture.

## Hebrew Product Boundary

Even though this vault is in English, the product answers are Hebrew. Hebrew answer quality is a core product requirement. If the text sounds translated, too formal, judgmental, or unclear, the implementation is not done.

## Avoid

- fake certainty
- long generic advice
- investment recommendations
- loan recommendations
- tax or legal advice
- claims that the employer can see personal data
- claims that the bot accessed real bank data

## Preferred Product Shape

The best answers are short, explain the decision, and point to a practical next step. The system should ask for missing data instead of guessing.

## Related Notes

- [[Hebrew Response Builder]]
- [[Safety Boundaries]]
- [[Data Readiness]]
