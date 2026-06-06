from app.ai.assistant_policy_schemas import (
    AnswerPlan,
    AssistantIntent,
    DataReadinessLevel,
    DataReadinessResult,
    FinancialContextSummary,
    ResponsePolicyDecision,
    ResponseType,
)


def test_response_policy_schema_enums_use_stable_lowercase_values() -> None:
    assert ResponseType.DIRECT_ANSWER.value == "direct_answer"
    assert ResponseType.CAUTIOUS_ESTIMATE.value == "cautious_estimate"
    assert ResponseType.ASK_FOR_MISSING_DATA.value == "ask_for_missing_data"
    assert ResponseType.CLARIFYING_QUESTION.value == "clarifying_question"
    assert ResponseType.UNSUPPORTED_REQUEST.value == "unsupported_request"
    assert ResponseType.PRIVACY_EXPLANATION.value == "privacy_explanation"
    assert ResponseType.ERROR_FALLBACK.value == "error_fallback"

    assert AssistantIntent.AFFORDABILITY_CHECK.value == "affordability_check"
    assert AssistantIntent.PAYMENT_SPLIT_SIMULATION.value == "payment_split_simulation"
    assert DataReadinessLevel.NONE.value == "none"


def test_financial_context_summary_accepts_partial_context_safely() -> None:
    summary = FinancialContextSummary.model_validate(
        {
            "has_transactions": True,
            "possible_duplicates": True,
            "unknown_extra_field": "ignored",
        }
    )

    assert summary.has_transactions is True
    assert summary.possible_duplicates is True
    assert summary.has_current_balance is None
    assert not hasattr(summary, "unknown_extra_field")


def test_policy_decision_and_answer_plan_have_safe_defaults() -> None:
    readiness = DataReadinessResult(
        level=DataReadinessLevel.NONE,
        can_answer=False,
    )
    decision = ResponsePolicyDecision(
        allowed=False,
        response_type=ResponseType.ASK_FOR_MISSING_DATA,
        data_readiness=readiness,
    )
    plan = AnswerPlan(
        response_type=decision.response_type,
        main_message_key="missing_data_required",
    )

    assert decision.missing_fields == []
    assert decision.required_disclaimers == []
    assert decision.must_include_uncertainty is False
    assert plan.numbers_to_include == {}
    assert plan.assumptions == []
    assert plan.tone == "practical_non_judgmental"
