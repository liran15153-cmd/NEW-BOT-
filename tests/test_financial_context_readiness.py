from app.ai.assistant_policy_schemas import AssistantIntent, DataReadinessLevel
from app.ai.financial_context_readiness import evaluate_financial_context_readiness


def test_no_financial_data_has_no_readiness_and_cannot_answer() -> None:
    result = evaluate_financial_context_readiness(
        None,
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
    )

    assert result.level == DataReadinessLevel.NONE
    assert result.can_answer is False
    assert result.missing_fields == ["financial_data"]
    assert result.must_include_uncertainty is True


def test_transactions_only_are_low_readiness_for_cashflow_questions() -> None:
    result = evaluate_financial_context_readiness(
        {"has_transactions": True},
        assistant_intent=AssistantIntent.CASHFLOW_STATUS,
    )

    assert result.level == DataReadinessLevel.LOW
    assert result.can_answer is False
    assert result.missing_fields == ["current_balance", "next_salary_date"]


def test_transactions_and_salary_without_live_balance_are_medium_readiness() -> None:
    result = evaluate_financial_context_readiness(
        {
            "has_transactions": True,
            "has_salary_date": True,
            "has_live_bank_data": False,
        },
        assistant_intent=AssistantIntent.AFFORDABILITY_CHECK,
    )

    assert result.level == DataReadinessLevel.MEDIUM
    assert result.can_answer is True
    assert result.must_include_uncertainty is True
    assert result.missing_fields == ["current_balance"]


def test_full_context_is_high_readiness_but_projections_still_need_uncertainty() -> None:
    result = evaluate_financial_context_readiness(
        {
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "has_recurring_expenses": True,
            "has_upcoming_expenses": True,
            "has_live_bank_data": True,
        },
        assistant_intent=AssistantIntent.PAYMENT_SPLIT_SIMULATION,
    )

    assert result.level == DataReadinessLevel.HIGH
    assert result.can_answer is True
    assert result.must_include_uncertainty is True
    assert result.missing_fields == []


def test_weekly_safe_spend_requires_balance_and_salary_context() -> None:
    result = evaluate_financial_context_readiness(
        {"has_transactions": True},
        assistant_intent=AssistantIntent.WEEKLY_SAFE_SPEND,
    )

    assert result.level == DataReadinessLevel.LOW
    assert result.can_answer is False
    assert result.missing_fields == ["current_balance", "next_salary_date"]


def test_overdraft_risk_requires_balance_and_salary_context() -> None:
    result = evaluate_financial_context_readiness(
        {"has_transactions": True},
        assistant_intent=AssistantIntent.OVERDRAFT_RISK,
    )

    assert result.level == DataReadinessLevel.LOW
    assert result.can_answer is False
    assert result.missing_fields == ["current_balance", "next_salary_date"]


def test_upcoming_expenses_requires_upcoming_expense_context() -> None:
    result = evaluate_financial_context_readiness(
        {
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
        },
        assistant_intent=AssistantIntent.UPCOMING_EXPENSES,
    )

    assert result.level == DataReadinessLevel.MEDIUM
    assert result.can_answer is False
    assert result.missing_fields == ["upcoming_expenses"]


def test_upcoming_expenses_with_full_context_can_answer_as_estimate() -> None:
    result = evaluate_financial_context_readiness(
        {
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "has_upcoming_expenses": True,
        },
        assistant_intent=AssistantIntent.UPCOMING_EXPENSES,
    )

    assert result.can_answer is True
    assert result.must_include_uncertainty is True
    assert result.missing_fields == []


def test_import_warnings_and_duplicates_force_uncertainty() -> None:
    result = evaluate_financial_context_readiness(
        {
            "has_transactions": True,
            "has_current_balance": True,
            "has_salary_date": True,
            "import_warnings": ["stale_import"],
            "possible_duplicates": True,
        },
        assistant_intent=AssistantIntent.RECURRING_EXPENSES,
    )

    assert result.must_include_uncertainty is True
    assert "stale_import" in result.warnings
    assert "possible_duplicates" in result.warnings
