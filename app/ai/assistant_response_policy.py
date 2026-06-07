from typing import Any

from pydantic import BaseModel

from app.ai.assistant_policy_schemas import (
    AssistantIntent,
    DataReadinessLevel,
    DataReadinessResult,
    FinancialContextSummary,
    ResponsePolicyDecision,
    ResponseType,
)
from app.ai.financial_context_readiness import evaluate_financial_context_readiness

_BLOCKED_REASONS = {
    AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE: "investment_advice_not_supported",
    AssistantIntent.UNSUPPORTED_LOAN_ADVICE: "loan_recommendation_not_supported",
    AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE: "tax_or_legal_advice_not_supported",
    AssistantIntent.SAFETY_BOUNDARY_REQUEST: "safety_boundary_not_supported",
}
_PROJECTION_INTENTS = {
    AssistantIntent.CASHFLOW_STATUS,
    AssistantIntent.WEEKLY_SAFE_SPEND,
    AssistantIntent.OVERDRAFT_RISK,
    AssistantIntent.AFFORDABILITY_CHECK,
    AssistantIntent.PAYMENT_SPLIT_SIMULATION,
}


def decide_response_policy(
    *,
    user_message: str,
    assistant_intent: AssistantIntent,
    financial_context_summary: FinancialContextSummary | dict | None,
    calculation_result: dict | BaseModel | None = None,
    missing_fields: list[str] | None = None,
) -> ResponsePolicyDecision:
    del user_message

    if assistant_intent in _BLOCKED_REASONS:
        return ResponsePolicyDecision(
            allowed=False,
            response_type=ResponseType.UNSUPPORTED_REQUEST,
            blocked_reason=_BLOCKED_REASONS[assistant_intent],
            reason="unsupported_financial_advice",
        )

    if assistant_intent == AssistantIntent.PRIVACY_QUESTION:
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.PRIVACY_EXPLANATION,
            reason="privacy_question",
        )

    if assistant_intent == AssistantIntent.UNKNOWN:
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.CLARIFYING_QUESTION,
            reason="unknown_intent",
        )

    if assistant_intent == AssistantIntent.GENERAL_HELP:
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.DIRECT_ANSWER,
            reason="general_help",
        )

    if missing_fields:
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.CLARIFYING_QUESTION,
            missing_fields=missing_fields,
            reason="missing_user_parameters",
        )

    if (
        assistant_intent
        in {
            AssistantIntent.RECURRING_EXPENSES,
            AssistantIntent.MONEY_LEAK_DETECTION,
            AssistantIntent.TRANSACTION_EXPLANATION,
        }
        and financial_context_summary is None
    ):
        readiness = DataReadinessResult(
            level=DataReadinessLevel.NONE,
            can_answer=False,
            missing_fields=["transactions"],
            must_include_uncertainty=True,
            reason="transaction_history_required",
        )
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.ASK_FOR_MISSING_DATA,
            missing_fields=["transactions"],
            required_disclaimers=["uncertainty_required"],
            must_include_uncertainty=True,
            reason="transaction_history_required",
            data_readiness=readiness,
        )

    readiness = evaluate_financial_context_readiness(
        financial_context_summary,
        assistant_intent=assistant_intent,
    )
    required_disclaimers = list(readiness.warnings)
    if readiness.must_include_uncertainty:
        required_disclaimers.append("uncertainty_required")

    if not readiness.can_answer:
        return ResponsePolicyDecision(
            allowed=True,
            response_type=ResponseType.ASK_FOR_MISSING_DATA,
            missing_fields=readiness.missing_fields,
            required_disclaimers=required_disclaimers,
            must_include_uncertainty=readiness.must_include_uncertainty,
            risk_level=_risk_level(calculation_result),
            reason=readiness.reason or "missing_required_financial_context",
            data_readiness=readiness,
        )

    response_type = (
        ResponseType.CAUTIOUS_ESTIMATE
        if readiness.must_include_uncertainty or assistant_intent in _PROJECTION_INTENTS
        else ResponseType.DIRECT_ANSWER
    )
    return ResponsePolicyDecision(
        allowed=True,
        response_type=response_type,
        missing_fields=readiness.missing_fields,
        required_disclaimers=required_disclaimers,
        must_include_uncertainty=readiness.must_include_uncertainty
        or assistant_intent in _PROJECTION_INTENTS,
        risk_level=_risk_level(calculation_result),
        reason=readiness.reason,
        data_readiness=readiness,
    )


def _risk_level(calculation_result: dict | BaseModel | None) -> str | None:
    if calculation_result is None:
        return None
    if isinstance(calculation_result, dict):
        risk_level = calculation_result.get("risk_level")
    else:
        risk_level = getattr(calculation_result, "risk_level", None)
    return _enum_or_string_value(risk_level)


def _enum_or_string_value(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)
