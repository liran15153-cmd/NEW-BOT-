from app.ai.assistant_policy_schemas import AssistantIntent, ResponseType
from app.ai.assistant_response_policy import decide_response_policy


def test_investment_loan_and_tax_or_legal_advice_are_blocked() -> None:
    investment = decide_response_policy(
        user_message="should I invest?",
        assistant_intent=AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE,
        financial_context_summary=None,
    )
    loan = decide_response_policy(
        user_message="should I take a loan?",
        assistant_intent=AssistantIntent.UNSUPPORTED_LOAN_ADVICE,
        financial_context_summary=None,
    )
    tax = decide_response_policy(
        user_message="is this tax advice?",
        assistant_intent=AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE,
        financial_context_summary=None,
    )

    assert investment.allowed is False
    assert investment.response_type == ResponseType.UNSUPPORTED_REQUEST
    assert investment.blocked_reason == "investment_advice_not_supported"
    assert loan.blocked_reason == "loan_recommendation_not_supported"
    assert tax.blocked_reason == "tax_or_legal_advice_not_supported"


def test_privacy_question_is_allowed_as_privacy_explanation() -> None:
    decision = decide_response_policy(
        user_message="does my employer see this?",
        assistant_intent=AssistantIntent.PRIVACY_QUESTION,
        financial_context_summary=None,
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.PRIVACY_EXPLANATION
    assert decision.reason == "privacy_question"


def test_cashflow_with_no_data_asks_for_missing_data() -> None:
    decision = decide_response_policy(
        user_message="until payday",
        assistant_intent=AssistantIntent.CASHFLOW_STATUS,
        financial_context_summary=None,
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.ASK_FOR_MISSING_DATA
    assert decision.missing_fields == ["financial_data"]
    assert decision.must_include_uncertainty is True


def test_affordability_with_partial_data_returns_cautious_estimate() -> None:
    decision = decide_response_policy(
        user_message="can I afford it?",
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
        financial_context_summary={
            "has_transactions": True,
            "has_salary_date": True,
            "has_live_bank_data": False,
        },
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.CAUTIOUS_ESTIMATE
    assert decision.must_include_uncertainty is True
    assert decision.missing_fields == ["current_balance"]


def test_recurring_expenses_without_transactions_asks_for_missing_data() -> None:
    decision = decide_response_policy(
        user_message="what subscriptions do I have?",
        assistant_intent=AssistantIntent.RECURRING_EXPENSES,
        financial_context_summary={"has_current_balance": True},
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.ASK_FOR_MISSING_DATA
    assert decision.missing_fields == ["transactions"]


def test_unknown_intent_asks_clarifying_question() -> None:
    decision = decide_response_policy(
        user_message="tell me a joke",
        assistant_intent=AssistantIntent.UNKNOWN,
        financial_context_summary=None,
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.CLARIFYING_QUESTION
    assert decision.reason == "unknown_intent"


def test_payment_split_missing_amount_or_months_asks_clarifying_question() -> None:
    decision = decide_response_policy(
        user_message="split it into payments",
        assistant_intent=AssistantIntent.PAYMENT_SPLIT_SIMULATION,
        financial_context_summary={
            "has_transactions": True,
            "has_salary_date": True,
            "has_live_bank_data": False,
        },
        missing_fields=["amount", "months"],
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.CLARIFYING_QUESTION
    assert decision.missing_fields == ["amount", "months"]


def test_full_financial_context_still_marks_projections_as_estimates() -> None:
    decision = decide_response_policy(
        user_message="can I afford it?",
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
        financial_context_summary={
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "has_recurring_expenses": True,
            "has_upcoming_expenses": True,
            "has_live_bank_data": True,
        },
    )

    assert decision.response_type == ResponseType.CAUTIOUS_ESTIMATE
    assert decision.must_include_uncertainty is True


def test_weekly_safe_spend_with_full_context_is_cautious_estimate() -> None:
    decision = decide_response_policy(
        user_message="how much can I safely spend this week?",
        assistant_intent=AssistantIntent.WEEKLY_SAFE_SPEND,
        financial_context_summary={
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "has_recurring_expenses": True,
            "has_upcoming_expenses": True,
            "has_live_bank_data": False,
        },
    )

    assert decision.allowed is True
    assert decision.response_type == ResponseType.CAUTIOUS_ESTIMATE
    assert decision.must_include_uncertainty is True


def test_import_warnings_force_uncertainty() -> None:
    decision = decide_response_policy(
        user_message="can I afford it?",
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
        financial_context_summary={
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "import_warnings": ["stale_import"],
        },
    )

    assert decision.must_include_uncertainty is True
    assert "stale_import" in decision.required_disclaimers
