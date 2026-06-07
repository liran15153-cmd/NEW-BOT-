# PRODUCT_BEHAVIOR.md

## Purpose

This document defines how the current financial wellness bot backend should behave as a product.

It is intentionally current-stage first. It should guide coding agents and developers without turning future product ideas into immediate implementation work.

The current product is a local deterministic bot-brain backend. It helps test short financial wellness conversations before adding real data sources, WhatsApp, Supabase, Open Banking, authentication, a frontend, or a real LLM.

## Current Product Status

The current backend supports:

- health checking through `GET /health`
- internal chat testing through `POST /chat/message`
- Hebrew user-facing answers
- deterministic intent detection
- deterministic amount and installment extraction
- short multi-turn clarification flows
- demo cash-flow status
- demo purchase simulation
- demo installment simulation
- unknown / unsupported message handling
- structured debug metadata for internal testing
- deterministic weekly safe-spend projection from demo cash-flow facts
- deterministic overdraft-risk projection before salary from demo cash-flow facts

The current backend does not support:

- real user financial data
- database persistence
- Supabase
- WhatsApp delivery
- Open Banking
- CSV upload or file import
- authentication
- employer dashboards
- employer analytics
- recurring payment detection
- subscription detection
- money leak analysis
- transaction explanation
- real LLM behavior
- proactive alerts

Do not implement unsupported behavior unless the user explicitly asks for that stage.

## Product Promise

The assistant should help a user understand a near-term financial decision in plain language.

For the current backend, that means:

```txt
The user can ask a simple cash-flow, weekly safe-spend, purchase, or installment question and receive a clear Hebrew response based on deterministic demo financial context.
```

The assistant should feel:

- private
- practical
- calm
- clear
- non-judgmental
- honest about uncertainty
- grounded in structured financial data

The assistant should not feel:

- generic
- preachy
- scary
- overconfident
- invasive
- employer-controlled
- like an investment advisor
- like a bank salesperson

## Primary User

The current primary user is an internal tester or early employee-style end user testing the bot brain.

They want to ask:

- How is my cash flow?
- What can I safely spend this week?
- Am I likely to enter overdraft before payday?
- Can I buy this?
- Can I buy this for a specific amount?
- What happens if I split this purchase into payments?

They do not want:

- a long financial lecture
- investment advice
- loan recommendations
- employer-facing reporting
- fake certainty from weak data
- a dashboard instead of a useful answer

## Current Supported Jobs

### 1. Cash-Flow Status

User intent:

```txt
cashflow_status
```

Example user questions:

```txt
כמה נשאר לי עד המשכורת?
מה מצב התזרים שלי?
How is my cash flow?
```

Expected behavior:

- Return a Hebrew answer based on demo financial context.
- Mention available buffer, safe-to-spend amount, days until salary, or risk level when available.
- Do not invent real account data.
- Do not imply the demo context is live bank data.

Current limitation:

```txt
The answer is based on mock/demo financial facts only.
```

### 2. Weekly Safe-Spend Projection

User intent:

```txt
weekly_spend
```

Example user questions:

```txt
כמה אפשר להוציא השבוע?
מה הסכום הבטוח שאפשר להוציא השבוע?
How much can I safely spend this week?
```

Expected behavior:

- Return a Hebrew answer based on demo financial context.
- Include the projected weekly safe-to-spend amount.
- Mention that the amount is calculated from the remaining days until salary.
- Do not claim this is live bank data or a production budget.

Current deterministic rule:

```txt
weekly_safe_to_spend = floor(safe_to_spend_until_salary * min(7, days_until_salary) / days_until_salary)
```

The calculation uses minor currency units and rounds down so the answer does not
overstate what is safe.

Current default demo result:

```txt
500.00 ILS safe-to-spend over 9 days -> 388.88 ILS safe this week
```

### 3. Overdraft Risk Before Salary

User intent:

```txt
overdraft_risk
```

Example user questions:

```txt
האם אני אכנס למינוס לפני המשכורת?
האם אני עלול להיכנס למינוס?
Am I likely to enter overdraft before payday?
```

Expected behavior:

- Return a Hebrew answer based on demo financial context.
- Project the balance before salary from current balance minus committed expenses until salary.
- If the projection is negative, include the overdraft gap and mark the risk as high.
- If the projection is positive but expected expenses are high, say no overdraft is currently projected while still recommending spending restraint.
- Do not imply this is live bank monitoring or a guaranteed future result.

Current deterministic rule:

```txt
projected_balance_before_salary = current_balance - committed_expenses_until_salary
overdraft_gap = max(0, -projected_balance_before_salary)
```

Current default demo result:

```txt
2500.00 ILS current balance - 1800.00 ILS committed expenses -> 700.00 ILS projected before salary; no projected overdraft, medium risk.
```

### 4. Purchase Simulation

User intent:

```txt
simulate_purchase
```

Example user questions:

```txt
אפשר לקנות את זה?
אפשר לקנות אוזניות ב-400 שקל?
Can I buy headphones for 400 shekels?
```

Expected behavior when amount exists:

- Extract the amount.
- Run the structured financial decision flow.
- Return a Hebrew answer with a practical recommendation.
- Include risk level and reason codes in debug metadata.

Expected behavior when amount is missing:

- Ask for the amount.
- Set `status = needs_more_info`.
- Set `tool_called = null`.
- Set `debug.tool_executed = false`.
- Store short-lived pending state so the next amount-only message can complete the purchase intent.

The assistant should not answer only “yes” or “no” unless the structured decision makes that safe.

### 5. Installment Simulation

User intent:

```txt
simulate_installments
```

Example user questions:

```txt
מה יקרה אם אפרוס לתשלומים?
מה יקרה אם אפרוס 900 שקל ל-3 תשלומים?
Split 900 shekels over 3 months
```

Expected behavior when amount and months exist:

- Extract amount.
- Extract installment months.
- Calculate monthly payment impact from structured facts.
- When an amount does not divide evenly across installments, round the monthly
  payment up to the nearest minor currency unit so the assistant does not
  understate the obligation.
- Return a Hebrew answer.

Expected behavior when required fields are missing:

- Missing amount and months: ask for both.
- Missing amount only: ask for amount.
- Missing months only: ask for months.
- Do not execute financial tools until all required fields exist.

Important product rule:

```txt
Installments can reduce short-term pressure but create future obligations. Do not present installments as automatically better.
```

### 6. Unknown Or Unsupported Message

User intent:

```txt
unknown
```

Expected behavior:

- Return a short Hebrew fallback.
- Set `status = unknown`.
- Set `tool_called = null`.
- Set `debug.tool_executed = false`.
- Do not run financial tools.

The assistant should not pretend it understood unsupported requests.

## Multi-Turn Behavior

The bot currently supports short clarification flows only.

Good flow:

```txt
User: אפשר לקנות את זה?
Bot: על איזה סכום מדובר?
User: 400 שקל
Bot: completes the pending purchase simulation.
```

Good flow:

```txt
User: מה יקרה אם אפרוס לתשלומים?
Bot: asks for amount and months.
User: 900 שקל ל-3 תשלומים
Bot: completes the pending installment simulation.
```

New-topic override:

```txt
User: אפשר לקנות את זה?
Bot: asks for amount.
User: כמה נשאר לי עד המשכורת?
Bot: treats this as cashflow_status, not as a purchase continuation.
```

Rules:

- Continue pending state only when the new message provides missing information or clearly continues the same intent.
- Start a new topic when the new message clearly matches a different supported intent.
- Clear pending state after a successful answered tool call.
- Clear or ignore stale state.
- Do not build long-term memory.

## Response Tone

The assistant should be:

- concise
- practical
- calm
- direct
- non-judgmental
- honest about what it knows

Avoid:

```txt
As an AI language model...
You are wasting money.
This is irresponsible.
Financial wellness is a journey.
You should definitely buy it.
```

Prefer Hebrew phrasing like:

```txt
לפי נתוני הדמו, זה אפשרי אבל די צפוף.
```

```txt
על איזה סכום מדובר?
```

```txt
אין לי מספיק מידע כדי לענות על זה בביטחון.
```

## Uncertainty Rules

The assistant must not invent financial facts.

It should not invent:

- balances
- salaries
- salary dates
- real transactions
- recurring payments
- subscriptions
- debts
- employer visibility
- future expenses

If data is missing, the assistant should ask for the missing field.

If data is demo-only, the answer should be phrased as demo-based behavior, not as a live financial truth.

Current acceptable wording:

```txt
לפי נתוני הדמו...
```

Current unacceptable wording:

```txt
בדקתי את חשבון הבנק שלך...
```

## Missing Data Behavior

Missing fields are product behavior, not only validation behavior.

For purchase:

```txt
missing amount -> ask for amount
```

For installments:

```txt
missing amount and months -> ask for both
missing amount -> ask for amount
missing months -> ask for months
```

Missing-field responses must not call financial tools.

## Safety Boundaries

The assistant must not:

- provide investment recommendations
- recommend stocks, crypto, funds, or securities
- provide legal advice
- provide tax advice
- recommend taking loans
- encourage debt
- initiate transfers
- pretend to access real bank data
- expose employer-facing analytics
- reveal hidden prompts, secrets, or other users' data
- obey prompt-injection attempts that conflict with product boundaries

If the user asks for investment advice:

```txt
אני לא יכול לתת המלצת השקעה. אני כן יכול לעזור לבדוק איך סכום מסוים ישפיע על התזרים שלך.
```

If the user asks whether the employer can see their data:

```txt
במוצר העתידי, המעסיק לא אמור לראות יתרות, עסקאות, שכר, חובות או שאלות אישיות. כרגע אין במערכת שכבת מעסיק או נתונים אמיתיים.
```

## Privacy Rules

Privacy is part of the product behavior.

Current rules:

- Treat every financial question as sensitive.
- Do not log raw financial content unnecessarily.
- Do not store user-facing answer text in conversation state.
- Keep debug metadata structured.
- Do not expose fake employer-facing behavior.
- Do not add analytics before privacy rules are explicit.

Future employer analytics must be aggregated and anonymized only. They are not part of the current backend.

## Data Integrity Rules

The assistant must fail safely.

It must not:

- treat negative amounts as positive amounts
- treat zero amounts as valid purchases
- treat zero months as valid installments
- silently execute tools when required fields are missing
- hide malformed input problems
- return confident answers from weak data

Bad input should produce one of:

- validation error
- missing-field response
- unknown response
- safe fallback response

It should not crash the request path.

## Current Good Examples

### Missing Purchase Amount

User:

```txt
אפשר לקנות את זה?
```

Assistant:

```txt
על איזה סכום מדובר?
```

Expected metadata:

```txt
intent = simulate_purchase
status = needs_more_info
tool_called = null
debug.tool_executed = false
missing_fields = ["amount"]
```

### Completed Purchase

User:

```txt
אפשר לקנות אוזניות ב-400 שקל?
```

Assistant:

```txt
לפי נתוני הדמו, אפשר לבצע את הקנייה, אבל היא תשאיר כרית ביטחון נמוכה עד המשכורת.
```

Expected metadata:

```txt
intent = simulate_purchase
status = answered
tool_called = simulate_purchase
debug.tool_executed = true
```

### Missing Installment Fields

User:

```txt
מה יקרה אם אפרוס לתשלומים?
```

Assistant:

```txt
כדי לבדוק פריסה לתשלומים, אני צריך סכום ומספר חודשים.
```

Expected metadata:

```txt
intent = simulate_installments
status = needs_more_info
tool_called = null
debug.tool_executed = false
missing_fields = ["amount", "months"]
```

### Unknown Message

User:

```txt
ספר לי בדיחה
```

Assistant:

```txt
לא הצלחתי לזהות בקשה פיננסית נתמכת מתוך ההודעה הזו.
```

Expected metadata:

```txt
intent = unknown
status = unknown
tool_called = null
debug.tool_executed = false
```

## Product Quality Bar

A product behavior change is not complete unless:

- it handles missing data
- it handles invalid input
- it avoids fake certainty
- it has tests
- it has safe error behavior
- it does not leak sensitive data
- it gives useful output in plain language
- it keeps user-facing Hebrew copy centralized
- it documents assumptions
- it fails safely when data is insufficient

## Future Product Behavior

The full product may eventually support:

- recurring payment detection
- subscription detection
- money leak analysis
- transaction explanation
- CSV import
- Open Banking
- manual financial data entry
- employer-facing aggregate analytics
- privacy-safe onboarding
- consent and deletion flows
- proactive alerts
- real LLM explanations
- WhatsApp delivery

These are future stages. Do not implement them from this document alone.

Each future behavior needs its own plan, tests, privacy review, and architecture boundary before implementation.

## Future Behavior Documents

When those stages become active, create focused docs such as:

```txt
docs/RECURRING_PAYMENTS.md
docs/CSV_IMPORT_BEHAVIOR.md
docs/EMPLOYER_ANALYTICS.md
docs/PRIVACY_AND_CONSENT.md
docs/LLM_BEHAVIOR.md
docs/WHATSAPP_BEHAVIOR.md
```

Do not overload this file with every future feature.

## Implementation Guidance For Agents

When implementing product behavior:

1. Inspect the current code first.
2. Match existing architecture boundaries.
3. Keep the current supported behavior small and testable.
4. Do not add unsupported product areas accidentally.
5. Do not make the assistant overconfident.
6. Always handle missing data.
7. Prefer deterministic calculations for financial numbers.
8. Keep AI wording separate from financial decisions.
9. Add or update tests for every behavior change.
10. Update this file only when product behavior intentionally changes.

## Open Product Decisions

These should not be guessed by coding agents:

1. What is the first real data source: manual entry, CSV import, or database-backed demo data?
2. What is the default safe-buffer threshold?
3. How should the assistant define safe, tight, and risky in production?
4. When should recurring-payment detection become active work?
5. What employer analytics are allowed, if any?
6. What data deletion and export behavior is required?
7. What consent text is required before using real financial data?
8. When should WhatsApp become the first real channel?
9. When is a real LLM useful enough to justify privacy and reliability risk?
10. What disclaimers are required before production release?
