# Financial Wellness Assistant Backend

Minimal FastAPI backend foundation for testing the bot brain without WhatsApp,
Open Banking, Supabase, auth, a database, file upload, frontend, or real LLM
integration.

## What It Does

- `GET /health` returns service health.
- `POST /chat/message` accepts an internal test chat message.
- A deterministic rule-based router detects one of four intents:
  - `cashflow_status`
  - `simulate_purchase`
  - `simulate_installments`
  - `unknown`
- Mock financial tools return structured demo answers.
- Tests cover the API contract, router parsing, and financial tool contracts.

## Setup

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

Then open:

```text
http://127.0.0.1:8000/health
```

## Example Chat Request

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/chat/message" `
  -ContentType "application/json" `
  -Body '{"user_id":"user_123","message":"Can I buy headphones for 400 shekels?"}'
```

Example response:

```json
{
  "answer": "Based on the demo financial context, this purchase is possible but would leave a low buffer until salary day.",
  "intent": "simulate_purchase",
  "tool_called": "simulate_purchase",
  "confidence": 0.85,
  "missing_fields": []
}
```

## Current Boundaries

This backend is intentionally deterministic. User messages are treated as
untrusted input and are parsed with small local rules only. Real financial data,
Supabase, WhatsApp, Open Banking, authentication, file upload, and LLM behavior
are deliberately deferred until this contract is stable.
