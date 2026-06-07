# Financial Wellness Assistant Backend

Python FastAPI backend for a deterministic Hebrew financial wellness bot brain.

This project is currently focused on the bot-brain foundation: intent parsing,
parameter extraction, short multi-turn dialogue, structured financial decisions,
and Hebrew response building. It intentionally does not include production data
infrastructure yet.

## Current Status

The backend currently supports:

- `GET /health`
- `POST /chat/message`
- local browser tester at `GET /tester`
- manual financial profile ingestion through `POST /financial/profile`
- deterministic intent parsing
- deterministic amount and installment extraction
- conservative installment monthly-payment calculation
- short in-memory multi-turn dialogue
- assistant response policy and data-readiness checks
- structured Pydantic request and response schemas
- structured financial tool contracts
- profile-backed financial tools using explicitly provided user data
- deterministic financial decision engine
- deterministic weekly safe-spend projection from stored profile facts
- deterministic overdraft-risk projection before salary from stored profile facts
- deterministic upcoming-expense pressure from stored committed obligations
- Hebrew user-facing answers
- internal debug metadata for testing
- pytest coverage for API, bot, dialogue, financial contracts, architecture, and
  audit behavior

The backend intentionally does not include:

- Supabase
- database
- WhatsApp
- Open Banking
- authentication
- file upload
- frontend
- admin dashboard
- real LLM integration
- external APIs
- background jobs

Those systems should stay deferred until the bot-brain contract is stable.

## Project Layout

```text
app/
  main.py
  api/
    chat_message_api.py
    financial_profile_api.py
    health_check_api.py
  ai/
    assistant_policy_schemas.py
    assistant_intent_classifier.py
    financial_context_readiness.py
    assistant_response_policy.py
    assistant_answer_plan.py
    financial_intent_parser.py
    financial_parameter_extractor.py
    hebrew_response_builder.py
    chat_router.py
    chat_message_schemas.py
    financial_tool_executor.py
  dialogue/
    conversation_flow_manager.py
    conversation_state.py
    conversation_state_store.py
  financial/
    financial_contracts.py
    financial_decision_engine.py
    demo_financial_tools.py
    user_financial_profile.py
    financial_reason_codes.py
  core/
    app_settings.py
    app_errors.py
docs/
  ARCHITECTURE.md
  PRODUCT_BEHAVIOR.md
  README.md
tests/
```

## Core Flow

```text
User message
  -> POST /chat/message
  -> ChatRouter
  -> assistant intent classifier and response policy
  -> intent parser
  -> parameter extractor
  -> dialogue manager
  -> missing-field validation
  -> financial context readiness check
  -> financial tool + decision engine, only when required fields exist
  -> answer planner
  -> Hebrew response builder
  -> structured response
```

Missing-field and unknown-intent cases must not call financial tools.
If no financial profile exists for the user, chat returns `needs_more_info`
instead of inventing balances, salary dates, or expenses.

## Supported Intents

```text
cashflow_status
weekly_spend
overdraft_risk
upcoming_expenses
simulate_purchase
simulate_installments
privacy_question
unsupported_investment_advice
unsupported_loan_advice
unsupported_tax_or_legal_advice
recurring_expenses
money_leak_detection
transaction_explanation
unknown
```

## Response Statuses

```text
answered
needs_more_info
unknown
error
```

Expected tool behavior:

- `answered`: `tool_called` is the executed tool name and
  `debug.tool_executed = true`
- `needs_more_info`: `tool_called = null` and `debug.tool_executed = false`
- `unknown`: `tool_called = null` and `debug.tool_executed = false`

## Manual Financial Profile

Before chat can answer projection or affordability questions, the current app
expects an explicit user financial profile. This is intentionally a real input
contract, not seeded production behavior.

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/financial/profile" `
  -ContentType "application/json" `
  -Body '{
    "user_id": "user_123",
    "as_of_date": "2026-06-07",
    "current_balance_minor": 250000,
    "next_salary_date": "2026-06-16",
    "safety_buffer_minor": 20000,
    "committed_obligations": [
      {
        "label": "rent",
        "amount_minor": 120000,
        "due_date": "2026-06-10",
        "currency": "ILS"
      }
    ]
  }'
```

The route validates required dates and rejects committed obligations whose
`due_date` is before `as_of_date`. Profiles are stored in memory only for the
current process. This is enough to exercise the real calculation path locally,
but it is not production persistence.

## Weekly Safe-Spend Projection

The backend supports questions such as:

```text
כמה אפשר להוציא השבוע?
How much can I safely spend this week?
```

The profile-backed tool computes this from the current balance, committed
obligations due by salary, and the configured safety buffer. It projects at most
the next 7 days, prorates the safe-to-spend amount over the remaining days until
salary using integer minor-unit math, and rounds the weekly cap down so the
assistant does not overstate what is safe.

In tests, the synthetic profile fixture uses `500.00 ILS` safe-to-spend over 9
days, which produces a weekly cap of `388.88 ILS`.

## Overdraft Risk Projection

The backend supports questions such as:

```text
האם אני אכנס למינוס לפני המשכורת?
Am I likely to enter overdraft before payday?
```

The profile-backed tool projects the balance before the next salary as:

```text
projected_balance_before_salary = current_balance - committed_expenses_until_salary
```

If the projection is negative, the result includes an `overdraft_gap_minor` and
the decision engine marks the risk as high. If the projection is positive but
expected expenses are high, the answer says no overdraft is currently projected
while still marking the risk as medium. This keeps "not projected to enter
overdraft" separate from "safe to spend freely".

The calculation uses the stored profile's current balance and committed
obligations due on or before `next_salary_date`. It does not use demo balances
unless a test explicitly injects a fixture.

## Upcoming Expense Pressure

The backend supports questions such as:

```text
איזה תשלומים קרובים יש לי?
What payments are coming soon?
```

The profile-backed tool reports near-term committed obligations without
pretending to have merchant names or live transaction history. It returns the
total upcoming expense amount in the next 7 days, the largest upcoming expense,
days until the next expense, projected balance after those near-term
commitments, and risk metadata.

The tool only uses obligations that the user profile supplied. It does not
invent subscription labels, merchant names, or transaction history.

## Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Run The API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Health check:

```text
http://127.0.0.1:8000/health
```

Local bot tester:

```text
http://127.0.0.1:8000/tester
```

## Open The Local Tester

The tester is a local browser app for manual bot-brain QA. It includes chat,
debug metadata, scenario buttons, transcript export, and a local-only file
sandbox preview.

From the project root:

```powershell
.\scripts\start_tester.ps1
```

The script starts the FastAPI server on `127.0.0.1:8000` if needed and opens the
tester page. If port `8000` is already occupied by another local app, it tries a
nearby fallback port and opens the tester there. It does not upload files or
connect to external services.

## Example Chat Request

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/chat/message" `
  -ContentType "application/json" `
  -Body '{"user_id":"user_123","session_id":"manual","message":"אפשר לקנות אוזניות ב-400 שקל?"}'
```

Example response shape:

```json
{
  "answer": "לפי הנתונים שסיפקת, קנייה של 400 ₪ אפשרית, אבל היא תשאיר כרית ביטחון נמוכה עד המשכורת.",
  "intent": "simulate_purchase",
  "status": "answered",
  "tool_called": "simulate_purchase",
  "confidence": 0.85,
  "missing_fields": [],
  "debug": {
    "session_id": "manual",
    "normalized_message": "אפשר לקנות אוזניות ב-400 שקל?",
    "matched_rule": "purchase_keyword",
    "parameters": {
      "amount_minor": 40000,
      "currency": "ILS",
      "months": null
    },
    "active_intent_before": null,
    "active_intent_after": null,
    "state_continued": false,
    "state_cleared": true,
    "tool_executed": true,
    "risk_level": "medium",
    "reason_codes": [
      "ENOUGH_BUFFER",
      "LOW_BUFFER_AFTER_PURCHASE",
      "MANY_DAYS_UNTIL_SALARY"
    ]
  }
}
```

## Multi-Turn Example

```text
User: אפשר לקנות את זה?
Bot: על איזה סכום מדובר?
User: 400 שקל
Bot: completes the pending purchase intent using the decision engine.
```

## Amount And Installment Parsing

Supported amount examples:

```text
400 שקל
400 ש"ח
400 שח
400 ₪
₪400
1,200 שקל
1200 שקל
400 nis
400 shekels
```

Supported installment examples:

```text
3 תשלומים
ל-3 תשלומים
ל־3 תשלומים
ב-3 תשלומים
ב־3 תשלומים
over 3 months
for 3 months
```

Invalid values such as negative amounts, zero amounts, and zero installment
months should not execute financial tools.

Installment simulations round the monthly payment up to the nearest minor
currency unit when the amount does not divide evenly across the number of
payments. This keeps affordability checks from understating future obligations.

## Architecture Rules

- API routes stay thin.
- `app/ai/chat_router.py` orchestrates only.
- User-facing Hebrew answer text belongs in `app/ai/hebrew_response_builder.py`.
- Hebrew parser keywords are allowed in `financial_intent_parser.py` and
  `financial_parameter_extractor.py`.
- Financial tools return structured facts only.
- The decision engine returns structured outcomes only.
- Conversation state is short-lived and in memory only.
- Debug metadata is internal testing metadata, not user-facing text.
- Policy, planner, financial modules, routes, and dialogue modules must not
  contain user-facing Hebrew answer copy.

## Documentation

- [Architecture](./ARCHITECTURE.md)
- [Product Behavior](./PRODUCT_BEHAVIOR.md)
- [Assistant Response Policy](./ASSISTANT_RESPONSE_POLICY.md)
- [Bot Answer Audit](./BOT_ANSWER_AUDIT.md)
- [Development Log](./development-log.md)

## Current Limitations

This backend stores manually posted financial profiles in memory only. It does
not access real accounts, persist data across process restarts, import files, or
call external AI providers.

Before release, the project still needs persistent storage, authentication,
consent, retention/deletion rules, and a safer ingestion path for real user
financial data.
