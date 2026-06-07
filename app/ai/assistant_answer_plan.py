from typing import Any

from pydantic import BaseModel

from app.ai.assistant_policy_schemas import (
    AnswerPlan,
    AssistantIntent,
    ResponsePolicyDecision,
    ResponseType,
)

_MESSAGE_KEYS = {
    ResponseType.DIRECT_ANSWER: "direct_answer",
    ResponseType.CAUTIOUS_ESTIMATE: "cautious_estimate",
    ResponseType.ASK_FOR_MISSING_DATA: "missing_data_required",
    ResponseType.CLARIFYING_QUESTION: "clarifying_question",
    ResponseType.UNSUPPORTED_REQUEST: "unsupported_financial_advice",
    ResponseType.PRIVACY_EXPLANATION: "privacy_explanation",
    ResponseType.ERROR_FALLBACK: "error_fallback",
}
_PROJECTION_INTENTS = {
    AssistantIntent.CASHFLOW_STATUS,
    AssistantIntent.WEEKLY_SAFE_SPEND,
    AssistantIntent.AFFORDABILITY_CHECK,
    AssistantIntent.PAYMENT_SPLIT_SIMULATION,
}
_FORBIDDEN_CLAIMS_BY_BLOCKED_REASON = {
    "investment_advice_not_supported": ["recommend_investment"],
    "loan_recommendation_not_supported": ["recommend_loan"],
    "tax_or_legal_advice_not_supported": ["provide_tax_or_legal_advice"],
}


def build_answer_plan(
    *,
    user_message: str,
    assistant_intent: AssistantIntent,
    response_policy_decision: ResponsePolicyDecision,
    financial_context_summary: dict | BaseModel | None = None,
    calculation_result: dict | BaseModel | None = None,
) -> AnswerPlan:
    del user_message, financial_context_summary

    required_disclaimer_keys = list(response_policy_decision.required_disclaimers)
    return AnswerPlan(
        response_type=response_policy_decision.response_type,
        main_message_key=_main_message_key(
            assistant_intent,
            response_policy_decision,
        ),
        numbers_to_include=_structured_numbers(calculation_result),
        assumptions=_assumptions(assistant_intent, response_policy_decision),
        warnings=_warnings(required_disclaimer_keys),
        missing_fields=list(response_policy_decision.missing_fields),
        forbidden_claims=_forbidden_claims(response_policy_decision),
        required_disclaimer_keys=required_disclaimer_keys,
    )


def _main_message_key(
    assistant_intent: AssistantIntent,
    decision: ResponsePolicyDecision,
) -> str:
    if (
        decision.response_type == ResponseType.ASK_FOR_MISSING_DATA
        and assistant_intent
        in {
            AssistantIntent.RECURRING_EXPENSES,
            AssistantIntent.MONEY_LEAK_DETECTION,
            AssistantIntent.TRANSACTION_EXPLANATION,
        }
    ):
        return "transaction_history_required"
    return _MESSAGE_KEYS[decision.response_type]


def _structured_numbers(calculation_result: dict | BaseModel | None) -> dict[str, Any]:
    if calculation_result is None:
        return {}
    if isinstance(calculation_result, dict):
        return dict(calculation_result)
    return calculation_result.model_dump(mode="json")


def _assumptions(
    assistant_intent: AssistantIntent,
    decision: ResponsePolicyDecision,
) -> list[str]:
    assumptions: list[str] = []
    if (
        decision.must_include_uncertainty
        or decision.response_type == ResponseType.CAUTIOUS_ESTIMATE
    ) and assistant_intent in _PROJECTION_INTENTS:
        assumptions.append("future_cashflow_is_estimate")
    return assumptions


def _warnings(required_disclaimer_keys: list[str]) -> list[str]:
    return [
        disclaimer
        for disclaimer in required_disclaimer_keys
        if disclaimer != "uncertainty_required"
    ]


def _forbidden_claims(decision: ResponsePolicyDecision) -> list[str]:
    forbidden_claims: list[str] = []
    if decision.blocked_reason is not None:
        forbidden_claims.extend(
            _FORBIDDEN_CLAIMS_BY_BLOCKED_REASON.get(decision.blocked_reason, [])
        )
    if decision.response_type == ResponseType.PRIVACY_EXPLANATION:
        forbidden_claims.append("expose_employee_financial_data_to_employer")
    return forbidden_claims
