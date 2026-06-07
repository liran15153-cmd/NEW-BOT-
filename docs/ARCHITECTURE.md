# ARCHITECTURE.md

## Purpose

This document defines the architecture rules for the current Python FastAPI financial wellness bot backend.

It is intentionally current-state first. It should guide coding agents and developers without giving them permission to add future infrastructure too early.

The current product is a local, deterministic bot-brain backend for testing financial wellness conversations. It is not yet a full production financial-data platform.

## Current System Status

The backend currently supports:

- `GET /health`
- `POST /chat/message`
- deterministic intent parsing
- deterministic parameter extraction
- short in-memory multi-turn dialogue
- structured financial contracts
- mock financial tools
- a deterministic financial decision engine
- deterministic weekly safe-spend projection from demo cash-flow facts
- deterministic overdraft-risk projection before salary from demo cash-flow facts
- Hebrew user-facing responses
- pytest coverage for API behavior, bot behavior, dialogue state, financial contracts, architecture boundaries, and audit checks

The backend does not currently include:

- database
- Supabase
- WhatsApp
- Open Banking
- authentication
- file upload
- frontend
- admin dashboard
- real LLM integration
- external APIs
- background jobs

Do not add any of those systems unless the user explicitly requests that stage and the current bot-brain contract is already stable.

## Architecture Principles

### 1. Keep routes thin

HTTP route handlers should only validate requests, access app-level dependencies, call the appropriate service/router, and return typed responses.

Business logic must not grow inside FastAPI route functions.

### 2. Keep deterministic financial logic outside AI wording

The bot may explain financial results, but it must not invent numbers.

Financial decisions should come from structured data and deterministic decision code. User-facing text should be generated only after structured results exist.

### 3. Keep user-facing Hebrew copy centralized

Hebrew answer text belongs in:

```txt
app/ai/hebrew_response_builder.py
```

Hebrew parser keywords are allowed in:

```txt
app/ai/financial_intent_parser.py
app/ai/financial_parameter_extractor.py
```

Do not put user-facing answer copy in financial tools, the decision engine, the router, API routes, or dialogue state.

### 4. Keep state short-lived and replaceable

Conversation state is currently in memory only. It exists to support short clarification flows such as:

```txt
User: Can I buy this?
Bot: What amount?
User: 400 shekels
Bot: completes the pending purchase check
```

State must not become long-term memory.

State must be injected or attached at app level so tests can reset it cleanly.

### 5. Treat financial data as sensitive even in demos

Even mock financial flows should follow privacy-safe habits:

- do not log raw financial questions unnecessarily
- do not expose sensitive values through debug text
- keep debug metadata structured
- do not store full user-facing answers in state
- do not add employer-facing analytics before privacy rules are explicit

### 6. Tests are part of the architecture

Every behavioral change should include tests. The project should stay easy to verify locally with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Current Module Ownership

### `app/main.py`

Creates the FastAPI app and attaches replaceable dependencies at app level:

- financial tools
- conversation state store
- financial decision engine

This keeps tests isolated and avoids uncontrolled global state.

### `app/api/`

Owns HTTP routes.

Current route files:

```txt
app/api/health_check_api.py
app/api/chat_message_api.py
```

API files should stay thin. They should not parse intents, calculate affordability, manage dialogue state, or build financial answers.

### `app/ai/`

Owns bot-brain orchestration and response construction.

Current responsibilities:

- parse intent
- extract parameters
- orchestrate dialogue and tool execution
- build structured chat responses
- keep Hebrew user-facing copy in one place

Current expected files:

```txt
app/ai/financial_intent_parser.py
app/ai/financial_parameter_extractor.py
app/ai/financial_tool_executor.py
app/ai/hebrew_response_builder.py
app/ai/chat_router.py
app/ai/chat_message_schemas.py
```

`app/ai/chat_router.py` should remain thin. It should orchestrate, not contain regex parsing rules or user-facing answer text.

### `app/dialogue/`

Owns short multi-turn state.

Current responsibilities:

- represent conversation state
- store state in memory
- decide whether to continue a pending intent or start a new topic
- clear stale or completed state

Current expected files:

```txt
app/dialogue/conversation_state.py
app/dialogue/conversation_state_store.py
app/dialogue/conversation_flow_manager.py
```

Dialogue code should not build Hebrew answers and should not perform financial calculations.

### `app/financial/`

Owns financial contracts, mock financial facts, reason codes, and deterministic decisions.

Current expected files:

```txt
app/financial/financial_contracts.py
app/financial/demo_financial_tools.py
app/financial/financial_decision_engine.py
app/financial/financial_reason_codes.py
```

Financial tools should return structured data only. They should not return user-facing answer strings.

The decision engine should return structured outcomes only:

- risk level
- reason codes
- recommended action
- computed amounts
- booleans such as `can_purchase`

It must not contain Hebrew or English user-facing copy.

### `app/core/`

Owns simple shared configuration and error helpers.

Do not turn `core` into a dumping ground. Add files here only when the concern is genuinely cross-cutting.

## Current Chat Flow

The expected `/chat/message` flow is:

```txt
request
  -> FastAPI validation
  -> ChatRouter
  -> parse intent
  -> extract parameters
  -> load conversation state
  -> dialogue manager resolves current turn
  -> compute missing fields
  -> execute financial tool and decision engine only when required fields exist
  -> response builder creates Hebrew answer
  -> update or clear conversation state
  -> return typed response
```

Missing-field cases must not call financial tools.

Unknown intent cases must not call financial tools.

Valid completed cases should set:

```txt
status = answered
tool_called = actual tool name
debug.tool_executed = true
```

Missing-field cases should set:

```txt
status = needs_more_info
tool_called = null
debug.tool_executed = false
```

Unknown cases should set:

```txt
status = unknown
tool_called = null
debug.tool_executed = false
```

## Request And Response Contract

Current chat request:

```json
{
  "user_id": "user_123",
  "session_id": "optional_session_id",
  "message": "Can I buy this for 400 shekels?"
}
```

`session_id` is optional. If absent, the backend should use a deterministic default session key based on `user_id`.

Current chat response must stay structured:

```json
{
  "answer": "Hebrew user-facing answer",
  "intent": "simulate_purchase",
  "status": "answered",
  "tool_called": "simulate_purchase",
  "confidence": 0.85,
  "missing_fields": [],
  "debug": {
    "session_id": "optional_session_id",
    "normalized_message": "normalized text",
    "matched_rule": "purchase_keyword",
    "parameters": {},
    "active_intent_before": null,
    "active_intent_after": null,
    "state_continued": false,
    "state_cleared": true,
    "tool_executed": true,
    "risk_level": "medium",
    "reason_codes": []
  }
}
```

Debug is internal metadata. Product behavior must not depend on debug fields.

Current executable financial intents:

```txt
cashflow_status
weekly_spend
overdraft_risk
simulate_purchase
simulate_installments
```

`weekly_spend` is a projection over the existing safe-to-spend amount until
salary. It must be calculated with integer minor-unit math and rounded down so
the assistant does not overstate what is safe to spend this week.

`overdraft_risk` is a projection over the current demo balance and committed
expenses until salary. It must report the projected balance before salary and an
overdraft gap only when the projection is negative. A positive projection with
high expected expenses can still be medium risk; do not collapse that into a
simple yes/no answer.

## Financial Model Rules

Money should be represented in minor units.

For ILS:

```txt
400 shekels -> 40000
```

Do not use floating-point arithmetic for stored or core calculated money amounts.

Current supported currency:

```txt
ILS
```

Current supported risk levels:

```txt
low
medium
high
```

Current supported chat statuses:

```txt
answered
needs_more_info
unknown
error
```

## Input Safety Rules

The backend should handle bad input safely:

- blank `user_id` should be rejected
- blank `message` should be rejected
- malformed JSON should be rejected
- unknown messages should not execute tools
- missing amount should not execute tools
- missing installment months should not execute tools
- negative amounts should not be treated as positive amounts
- zero amounts and zero months should not execute tools
- very long unusual messages should return controlled responses
- prompt-injection-style messages should not bypass deterministic routing or access hidden data

## Testing Rules

The minimum test set should cover:

- health endpoint
- chat endpoint response contract
- intent parsing
- amount parsing
- installment parsing
- missing-field behavior
- unknown behavior
- multi-turn continuation
- new-topic override
- state expiry and reset
- no tool execution for incomplete requests
- decision engine outputs
- Hebrew answer boundary
- architecture guardrails
- bad-input behavior
- bounded local stress behavior

Current tests should remain local and deterministic. Do not require real bank data, real AI calls, external APIs, WhatsApp, or Supabase to run the test suite.

## Security And Privacy Rules

Until real user data exists, keep these rules as implementation blockers for future stages:

- never commit secrets
- never expose service keys client-side
- do not log raw financial data
- do not store raw uploaded files without a retention policy
- do not expose employee-level financial data to employers
- do not add employer analytics before anonymization rules are explicit
- treat AI-generated or user-provided content as untrusted input
- validate all external input at boundaries

## What Not To Build Yet

Do not add the following from this architecture file unless a future task explicitly asks for that stage:

```txt
Supabase
database models
repositories
CSV upload
Open Banking
WhatsApp
real LLM provider
provider adapters
authentication
frontend
admin dashboard
background jobs
employer analytics
long-term memory
```

These are future product stages, not current implementation instructions.

## Near-Term Architecture Direction

The next useful architecture work should focus on the bot brain, not infrastructure.

Recommended next stages:

1. Improve deterministic intent and parameter coverage with tests.
2. Add richer financial decision scenarios using mock/demo facts.
3. Add confidence and uncertainty handling for incomplete demo data.
4. Add explicit unsupported-intent handling.
5. Add more bad-input and stress tests.
6. Only after that, decide whether the next real data source should be manual input, CSV import, or Supabase-backed persistence.

## Future Architecture Notes

The long-term production product may eventually need:

- persistent users
- database-backed transactions
- import batches
- recurring expense detection
- cash-flow projections
- consent-based Open Banking
- WhatsApp delivery
- authentication
- deletion/export flows
- aggregated employer analytics
- observability and request IDs
- background jobs for imports and cleanup

Those systems should be designed in separate documents when they become active work:

```txt
docs/DATA_MODEL.md
docs/SECURITY_AND_PRIVACY.md
docs/TESTING_STRATEGY.md
docs/API_CONTRACTS.md
docs/INTEGRATIONS.md
docs/PRODUCT_BEHAVIOR.md
```

Do not implement future folders just because they are listed here.

## Code Change Rules For Agents

When modifying this project:

1. Inspect relevant files first.
2. Keep changes small and focused.
3. Preserve current module boundaries.
4. Do not rewrite architecture unless explicitly asked.
5. Do not add dependencies unless justified.
6. Do not add deferred integrations by accident.
7. Do not modify `.venv`, `.tmp`, generated files, database files, or secrets.
8. Add or update tests for behavior changes.
9. Update documentation when behavior or architecture changes.
10. Run the relevant tests before claiming completion.
11. Report files changed, tests run, risks, and follow-ups.

## Definition Of Done

A backend change is complete only when:

- the relevant code path works locally
- relevant tests pass
- errors are handled clearly
- sensitive data is not logged
- financial calculations stay deterministic where possible
- API behavior is documented if changed
- the change does not break existing flows
- assumptions are documented
- remaining risks are clearly stated

## Open Decisions

These are intentionally unresolved and should not be guessed by coding agents:

1. What is the first real data source: manual entry, CSV import, or database-backed demo data?
2. When should Supabase be introduced, if at all?
3. What authentication model is appropriate for employees?
4. What financial data retention policy is acceptable?
5. What user deletion/export behavior is required?
6. What employer analytics are safe and useful?
7. What compliance requirements apply before launch?
8. Which production messaging channel comes first?
9. When is a real LLM useful enough to justify the added privacy and reliability risk?
10. What accuracy threshold is required for recurring-payment detection?

