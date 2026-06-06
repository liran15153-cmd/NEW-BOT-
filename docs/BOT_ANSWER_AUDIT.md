# BOT_ANSWER_AUDIT.md

## Purpose

This document records a deterministic answer audit for the local FastAPI financial wellness bot backend. The bot is not connected to an LLM, so the audit checks routing, policy decisions, tool execution, missing-data behavior, and Hebrew answer quality inside the current supported scope.

## What The Bot Can Answer Today

- Demo cash-flow status questions.
- Demo purchase affordability questions with an amount.
- Demo installment simulations with amount and number of payments.
- Short multi-turn clarification flows for missing amount or months.
- Privacy questions about employer visibility.
- Unsupported investment, loan, tax, and legal advice requests.
- Future-feature requests for subscriptions, money leaks, and transaction explanations by asking for transaction history instead of faking analysis.

## What The Bot Cannot Answer Yet

- Open-ended general conversation.
- Real bank balances, salary dates, transactions, subscriptions, or debts.
- Real recurring-payment detection or money-leak analysis.
- Tax, legal, investment, or loan recommendations.
- Any answer requiring a real LLM, database, Open Banking, Supabase, WhatsApp, file upload, or external API.

## Safety Findings And Fixes

- Prompt-injection-style requests are treated as `safety_boundary_request` and do not execute tools.
- Core answered and missing-field flows expose response-policy metadata in `debug`.
- Hebrew answer text remains centralized in `app/ai/hebrew_response_builder.py`.
- Future-feature requests ask for missing transaction history instead of pretending to analyze unavailable data.

## Commands Used

```powershell
.\.venv\Scripts\python.exe scripts\audit_bot_answers.py --markdown docs\BOT_ANSWER_AUDIT.md
.\.venv\Scripts\python.exe -m pytest -q
```

## Current Audit Result

Flagged cases: `0`

## Scenario Matrix

case_id | intent | status | tool_called | tool_executed | missing_fields | assistant_intent | response_type | pass_or_flag
------- | ------ | ------ | ----------- | ------------- | -------------- | ---------------- | ------------- | ------------
cashflow_he | cashflow_status | answered | cashflow_status | True |  | cashflow_status | cautious_estimate | PASS
cashflow_en | cashflow_status | answered | cashflow_status | True |  | cashflow_status | cautious_estimate | PASS
purchase_he | simulate_purchase | answered | simulate_purchase | True |  | affordability_check | cautious_estimate | PASS
purchase_missing | simulate_purchase | needs_more_info |  | False | amount | affordability_check | clarifying_question | PASS
installments_he | simulate_installments | answered | simulate_installments | True |  | payment_split_simulation | cautious_estimate | PASS
privacy_he | privacy_question | answered |  | False |  | privacy_question | privacy_explanation | PASS
loan_he | unsupported_loan_advice | answered |  | False |  | unsupported_loan_advice | unsupported_request | PASS
subscriptions_he | recurring_expenses | needs_more_info |  | False | transactions | recurring_expenses | ask_for_missing_data | PASS
prompt_injection_balance | safety_boundary_request | answered |  | False |  | safety_boundary_request | unsupported_request | PASS
prompt_injection_purchase | safety_boundary_request | answered |  | False |  | safety_boundary_request | unsupported_request | PASS
unknown_joke | unknown | unknown |  | False |  |  |  | PASS

## Notes

- This audit uses the local FastAPI app through TestClient.
- It does not call an LLM, database, external API, or running server.
- `FLAG` means the deterministic response did not match the expected audit contract.
