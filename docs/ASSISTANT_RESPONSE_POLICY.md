# ASSISTANT_RESPONSE_POLICY.md

## Purpose

This document defines Assistant Response Policy v1 for the current Python
FastAPI financial wellness bot backend.

The policy layer decides what kind of response is safe before the final Hebrew
answer is written. It is deterministic, local, and testable.

This is not the Hebrew QA pass. The Hebrew QA pass is future work.

## What This Layer Does

The response policy layer:

- classifies broad assistant intents
- blocks unsupported financial advice
- recognizes privacy questions
- checks whether financial context is sufficient
- marks weak or partial data as uncertain
- decides whether to answer, ask for missing data, ask a clarifying question, or
  return a safe unsupported-response
- creates a structured answer plan for the Hebrew response builder
- exposes structured policy metadata in `debug`

## What This Layer Does Not Do

The response policy layer must not:

- generate final Hebrew copy
- invent balances, transactions, salary dates, subscriptions, or calculations
- call external APIs
- call an LLM
- access a database
- execute financial tools directly
- store conversation state
- pretend future features are already implemented

## Current Modules

Current policy modules live inside the existing bot-brain package:

```text
app/ai/assistant_policy_schemas.py
app/ai/assistant_intent_classifier.py
app/ai/financial_context_readiness.py
app/ai/assistant_response_policy.py
app/ai/assistant_answer_plan.py
```

Do not create a parallel `app/assistant` package for this layer.

## Response Types

Supported response types:

```text
direct_answer
cautious_estimate
ask_for_missing_data
clarifying_question
unsupported_request
privacy_explanation
error_fallback
```

Projection-style financial answers should normally be cautious estimates, even
when the user profile context is complete. Future cash flow is not guaranteed.

## Assistant Intents

Policy-level assistant intents:

```text
cashflow_status
affordability_check
payment_split_simulation
recurring_expenses
money_leak_detection
transaction_explanation
privacy_question
unsupported_investment_advice
unsupported_loan_advice
unsupported_tax_or_legal_advice
general_help
unknown
```

Only these map to executable current tools:

```text
cashflow_status -> cashflow_status
affordability_check -> simulate_purchase
payment_split_simulation -> simulate_installments
```

Future product intents such as recurring expenses and money leak detection are
recognized, but they do not execute tools yet.

## Data Readiness Levels

Readiness levels:

```text
none
low
medium
high
```

Basic meaning:

- `none`: no usable financial data
- `low`: partial data exists, but not enough for core cash-flow decisions
- `medium`: useful estimate may be possible, but uncertainty is required
- `high`: stronger context exists, but projections still need uncertainty

Warnings such as possible duplicates or stale imports force uncertainty.

## Safety Rules

The assistant must not:

- recommend investments
- recommend taking loans
- provide tax or legal advice
- present estimates as guaranteed facts
- imply it accessed live bank data when only manual profile data exists
- execute financial tools when required user parameters are missing
- execute financial tools when required financial profile data is missing
- execute financial tools for privacy, unsupported-advice, or future-feature
  requests

Unsupported and privacy responses are still useful answers, but they do not call
financial tools.

## Hebrew Response Boundary

All user-facing Hebrew answer text belongs in:

```text
app/ai/hebrew_response_builder.py
```

Hebrew parser keywords are allowed in:

```text
app/ai/assistant_intent_classifier.py
app/ai/financial_intent_parser.py
app/ai/financial_parameter_extractor.py
```

Policy, planner, financial tools, decision engine, router, and API routes must
not contain user-facing Hebrew answer copy.

## Current Limitations

The policy layer currently evaluates manually posted financial profile context.
It does not connect to real accounts, file imports, Supabase, WhatsApp, Open
Banking, a persistent database, or an LLM.

Recurring expenses, money leaks, and transaction explanations are recognized as
future product intents. They currently ask for transaction history instead of
pretending to analyze unavailable data.

## Future Hebrew QA Pass

The future Hebrew QA pass should run after the response builder creates a draft
answer. It should check tone, clarity, Hebrew quality, and unsafe phrasing.

It should not replace the deterministic policy layer. Policy decisions must stay
structured and testable.
