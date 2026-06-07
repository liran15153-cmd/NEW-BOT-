from app.ai.assistant_answer_plan import build_answer_plan
from app.ai.assistant_policy_schemas import (
    AssistantIntent,
    DataReadinessLevel,
    DataReadinessResult,
    ResponsePolicyDecision,
    ResponseType,
)


def test_missing_data_plan_contains_missing_fields() -> None:
    decision = ResponsePolicyDecision(
        allowed=True,
        response_type=ResponseType.ASK_FOR_MISSING_DATA,
        missing_fields=["current_balance", "next_salary_date"],
        data_readiness=DataReadinessResult(
            level=DataReadinessLevel.LOW,
            can_answer=False,
        ),
    )

    plan = build_answer_plan(
        user_message="until payday",
        assistant_intent=AssistantIntent.CASHFLOW_STATUS,
        response_policy_decision=decision,
    )

    assert plan.main_message_key == "missing_data_required"
    assert plan.missing_fields == ["current_balance", "next_salary_date"]


def test_cautious_estimate_plan_contains_uncertainty_disclaimer_key() -> None:
    decision = ResponsePolicyDecision(
        allowed=True,
        response_type=ResponseType.CAUTIOUS_ESTIMATE,
        required_disclaimers=["uncertainty_required"],
        must_include_uncertainty=True,
    )

    plan = build_answer_plan(
        user_message="can I afford it?",
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
        response_policy_decision=decision,
    )

    assert plan.main_message_key == "cautious_estimate"
    assert "uncertainty_required" in plan.required_disclaimer_keys
    assert "future_cashflow_is_estimate" in plan.assumptions


def test_overdraft_risk_plan_contains_projection_assumption() -> None:
    decision = ResponsePolicyDecision(
        allowed=True,
        response_type=ResponseType.CAUTIOUS_ESTIMATE,
        required_disclaimers=["uncertainty_required"],
        must_include_uncertainty=True,
    )

    plan = build_answer_plan(
        user_message="will I enter overdraft before payday?",
        assistant_intent=AssistantIntent.OVERDRAFT_RISK,
        response_policy_decision=decision,
    )

    assert plan.main_message_key == "cautious_estimate"
    assert "future_cashflow_is_estimate" in plan.assumptions


def test_unsupported_request_plan_contains_forbidden_claims() -> None:
    decision = ResponsePolicyDecision(
        allowed=False,
        response_type=ResponseType.UNSUPPORTED_REQUEST,
        blocked_reason="investment_advice_not_supported",
    )

    plan = build_answer_plan(
        user_message="should I invest?",
        assistant_intent=AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE,
        response_policy_decision=decision,
    )

    assert plan.main_message_key == "unsupported_financial_advice"
    assert "recommend_investment" in plan.forbidden_claims


def test_privacy_plan_forbids_employer_financial_data_exposure() -> None:
    decision = ResponsePolicyDecision(
        allowed=True,
        response_type=ResponseType.PRIVACY_EXPLANATION,
    )

    plan = build_answer_plan(
        user_message="does my employer see this?",
        assistant_intent=AssistantIntent.PRIVACY_QUESTION,
        response_policy_decision=decision,
    )

    assert plan.main_message_key == "privacy_explanation"
    assert "expose_employee_financial_data_to_employer" in plan.forbidden_claims


def test_plan_includes_structured_calculation_numbers_without_user_facing_copy() -> None:
    decision = ResponsePolicyDecision(
        allowed=True,
        response_type=ResponseType.CAUTIOUS_ESTIMATE,
        required_disclaimers=["stale_import"],
    )

    plan = build_answer_plan(
        user_message="can I afford it?",
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
        response_policy_decision=decision,
        calculation_result={
            "amount_minor": 40000,
            "safe_to_spend_minor": 60000,
        },
    )

    assert plan.numbers_to_include["amount_minor"] == 40000
    assert plan.numbers_to_include["safe_to_spend_minor"] == 60000
    assert plan.warnings == ["stale_import"]
