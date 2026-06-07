import pytest

from app.financial.financial_contracts import (
    CashflowStatusInput,
    Currency,
    InstallmentsSimulationInput,
    OverdraftRiskInput,
    PurchaseSimulationInput,
    UpcomingExpensesInput,
    WeeklySpendInput,
)
from app.financial.user_financial_profile import (
    FinancialObligation,
    FinancialProfileSnapshot,
    InMemoryFinancialProfileStore,
    MissingFinancialDataError,
    UserFinancialTools,
    financial_context_summary,
)


def test_user_financial_tools_calculate_cashflow_from_stored_profile() -> None:
    tools = _tools_with_profile(_profile())

    result = tools.cashflow_status(CashflowStatusInput(user_id="profile_user"))

    assert result.current_balance_minor == 250000
    assert result.committed_expenses_minor == 150000
    assert result.available_buffer_minor == 100000
    assert result.safe_to_spend_minor == 80000
    assert result.days_until_salary == 9
    assert result.currency == Currency.ILS
    assert result.expected_expenses_high is True


def test_user_financial_tools_calculate_weekly_projection_from_profile() -> None:
    tools = _tools_with_profile(_profile())

    result = tools.weekly_spend(WeeklySpendInput(user_id="profile_user"))

    assert result.safe_to_spend_until_salary_minor == 80000
    assert result.daily_safe_to_spend_minor == 8888
    assert result.weekly_safe_to_spend_minor == 62222
    assert result.projected_buffer_after_weekly_spend_minor == 37778
    assert result.days_until_salary == 9
    assert result.projection_days == 7


def test_user_financial_tools_calculate_overdraft_and_upcoming_expenses() -> None:
    tools = _tools_with_profile(_profile())

    overdraft = tools.overdraft_risk(OverdraftRiskInput(user_id="profile_user"))
    upcoming = tools.upcoming_expenses(UpcomingExpensesInput(user_id="profile_user"))

    assert overdraft.projected_balance_before_salary_minor == 100000
    assert overdraft.overdraft_gap_minor == 0
    assert overdraft.committed_expenses_until_salary_minor == 150000
    assert upcoming.upcoming_expenses_next_7_days_minor == 150000
    assert upcoming.largest_upcoming_expense_minor == 120000
    assert upcoming.days_until_next_expense == 3
    assert upcoming.upcoming_expense_count == 2
    assert upcoming.projected_balance_after_upcoming_minor == 100000
    assert upcoming.safe_to_spend_minor == 80000


def test_user_financial_tools_calculate_purchase_and_installments() -> None:
    tools = _tools_with_profile(_profile())

    purchase = tools.simulate_purchase(
        PurchaseSimulationInput(user_id="profile_user", amount_minor=40000)
    )
    installments = tools.simulate_installments(
        InstallmentsSimulationInput(
            user_id="profile_user",
            amount_minor=90000,
            months=3,
        )
    )

    assert purchase.available_buffer_before_purchase_minor == 100000
    assert purchase.safe_to_spend_minor == 80000
    assert purchase.buffer_after_purchase_minor == 60000
    assert installments.monthly_payment_minor == 30000
    assert installments.available_buffer_before_payment_minor == 100000
    assert installments.safe_to_spend_minor == 80000
    assert installments.buffer_after_monthly_payment_minor == 70000


def test_user_financial_tools_raise_missing_data_for_unknown_user() -> None:
    tools = UserFinancialTools(InMemoryFinancialProfileStore())

    with pytest.raises(MissingFinancialDataError) as exc_info:
        tools.cashflow_status(CashflowStatusInput(user_id="unknown_user"))

    assert exc_info.value.missing_fields == ["financial_data"]
    assert exc_info.value.reason == "no_financial_profile"


def test_empty_obligation_profile_is_known_context_not_missing_context() -> None:
    profile = FinancialProfileSnapshot(
        user_id="empty_obligations_user",
        as_of_date="2026-06-07",
        current_balance_minor=250000,
        next_salary_date="2026-06-16",
        safety_buffer_minor=20000,
        committed_obligations=[],
    )
    tools = _tools_with_profile(profile)

    upcoming = tools.upcoming_expenses(
        UpcomingExpensesInput(user_id="empty_obligations_user")
    )
    summary = financial_context_summary(profile)

    assert upcoming.upcoming_expenses_next_7_days_minor == 0
    assert upcoming.upcoming_expense_count == 0
    assert upcoming.days_until_next_expense == 0
    assert summary["has_upcoming_expenses"] is True


def test_profile_rejects_committed_obligations_before_profile_date() -> None:
    with pytest.raises(ValueError, match="committed_obligations"):
        FinancialProfileSnapshot(
            user_id="invalid_obligation_user",
            as_of_date="2026-06-07",
            current_balance_minor=250000,
            next_salary_date="2026-06-16",
            safety_buffer_minor=20000,
            committed_obligations=[
                FinancialObligation(
                    label="past charge",
                    amount_minor=12000,
                    due_date="2026-06-01",
                )
            ],
        )


def _tools_with_profile(profile: FinancialProfileSnapshot) -> UserFinancialTools:
    store = InMemoryFinancialProfileStore()
    store.save(profile)
    return UserFinancialTools(store)


def _profile() -> FinancialProfileSnapshot:
    return FinancialProfileSnapshot(
        user_id="profile_user",
        as_of_date="2026-06-07",
        current_balance_minor=250000,
        next_salary_date="2026-06-16",
        safety_buffer_minor=20000,
        committed_obligations=[
            FinancialObligation(
                label="rent",
                amount_minor=120000,
                due_date="2026-06-10",
            ),
            FinancialObligation(
                label="utilities",
                amount_minor=30000,
                due_date="2026-06-12",
            ),
            FinancialObligation(
                label="after salary",
                amount_minor=40000,
                due_date="2026-06-20",
            ),
        ],
    )
