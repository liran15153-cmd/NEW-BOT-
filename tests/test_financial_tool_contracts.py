from app.financial.financial_contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    CashflowStatusTool,
    Currency,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    InstallmentsSimulationTool,
    OverdraftRiskInput,
    OverdraftRiskResult,
    OverdraftRiskTool,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
    PurchaseSimulationTool,
    UpcomingExpensesInput,
    UpcomingExpensesResult,
    UpcomingExpensesTool,
    WeeklySpendInput,
    WeeklySpendResult,
    WeeklySpendTool,
)
from app.financial.demo_financial_tools import DemoFinancialTools


def test_demo_tools_satisfy_financial_protocols() -> None:
    tools = DemoFinancialTools()

    assert isinstance(tools, CashflowStatusTool)
    assert isinstance(tools, PurchaseSimulationTool)
    assert isinstance(tools, InstallmentsSimulationTool)
    assert isinstance(tools, WeeklySpendTool)
    assert isinstance(tools, OverdraftRiskTool)
    assert isinstance(tools, UpcomingExpensesTool)


def test_financial_result_models_are_structured_data_without_answers() -> None:
    cashflow = CashflowStatusResult(
        current_balance_minor=250000,
        committed_expenses_minor=180000,
        available_buffer_minor=70000,
        safe_to_spend_minor=50000,
        days_until_salary=9,
        currency=Currency.ILS,
        expected_expenses_high=True,
    )
    purchase = PurchaseSimulationResult(
        amount_minor=40000,
        currency=Currency.ILS,
        available_buffer_before_purchase_minor=70000,
        safe_to_spend_minor=50000,
        buffer_after_purchase_minor=30000,
        days_until_salary=9,
    )
    installments = InstallmentsSimulationResult(
        amount_minor=90000,
        months=3,
        monthly_payment_minor=30000,
        currency=Currency.ILS,
        available_buffer_before_payment_minor=70000,
        safe_to_spend_minor=50000,
        buffer_after_monthly_payment_minor=40000,
        days_until_salary=9,
    )
    weekly_spend = WeeklySpendResult(
        available_buffer_minor=70000,
        safe_to_spend_until_salary_minor=50000,
        daily_safe_to_spend_minor=5555,
        weekly_safe_to_spend_minor=38888,
        projected_buffer_after_weekly_spend_minor=31112,
        days_until_salary=9,
        projection_days=7,
        currency=Currency.ILS,
        expected_expenses_high=True,
    )
    overdraft = OverdraftRiskResult(
        current_balance_minor=250000,
        committed_expenses_until_salary_minor=180000,
        projected_balance_before_salary_minor=70000,
        overdraft_gap_minor=0,
        days_until_salary=9,
        currency=Currency.ILS,
        expected_expenses_high=True,
    )
    upcoming = UpcomingExpensesResult(
        current_balance_minor=250000,
        upcoming_expenses_next_7_days_minor=65000,
        largest_upcoming_expense_minor=45000,
        days_until_next_expense=2,
        upcoming_expense_count=3,
        projected_balance_after_upcoming_minor=185000,
        available_buffer_until_salary_minor=70000,
        safe_to_spend_minor=50000,
        lookahead_days=7,
        days_until_salary=9,
        currency=Currency.ILS,
        expected_expenses_high=True,
    )

    assert "answer" not in CashflowStatusResult.model_fields
    assert "answer" not in PurchaseSimulationResult.model_fields
    assert "answer" not in InstallmentsSimulationResult.model_fields
    assert "answer" not in WeeklySpendResult.model_fields
    assert "answer" not in OverdraftRiskResult.model_fields
    assert "answer" not in UpcomingExpensesResult.model_fields
    assert "risk_level" not in CashflowStatusResult.model_fields
    assert "risk_level" not in PurchaseSimulationResult.model_fields
    assert "risk_level" not in InstallmentsSimulationResult.model_fields
    assert "risk_level" not in WeeklySpendResult.model_fields
    assert "risk_level" not in OverdraftRiskResult.model_fields
    assert "risk_level" not in UpcomingExpensesResult.model_fields
    assert cashflow.safe_to_spend_minor == 50000
    assert purchase.currency == Currency.ILS
    assert installments.months == 3
    assert weekly_spend.weekly_safe_to_spend_minor == 38888
    assert overdraft.projected_balance_before_salary_minor == 70000
    assert upcoming.upcoming_expenses_next_7_days_minor == 65000


def test_demo_cashflow_status_returns_structured_result() -> None:
    tools = DemoFinancialTools()

    result = tools.cashflow_status(CashflowStatusInput(user_id="user_123"))

    assert result.available_buffer_minor == 70000
    assert result.safe_to_spend_minor == 50000
    assert result.days_until_salary == 9
    assert result.expected_expenses_high is True
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_weekly_spend_returns_conservative_projection() -> None:
    tools = DemoFinancialTools()

    result = tools.weekly_spend(WeeklySpendInput(user_id="user_123"))

    assert result.safe_to_spend_until_salary_minor == 50000
    assert result.daily_safe_to_spend_minor == 5555
    assert result.weekly_safe_to_spend_minor == 38888
    assert result.projected_buffer_after_weekly_spend_minor == 31112
    assert result.projection_days == 7
    assert result.days_until_salary == 9
    assert result.expected_expenses_high is True
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_overdraft_risk_projects_balance_until_salary() -> None:
    tools = DemoFinancialTools()

    result = tools.overdraft_risk(OverdraftRiskInput(user_id="user_123"))

    assert result.current_balance_minor == 250000
    assert result.committed_expenses_until_salary_minor == 180000
    assert result.projected_balance_before_salary_minor == 70000
    assert result.overdraft_gap_minor == 0
    assert result.days_until_salary == 9
    assert result.expected_expenses_high is True
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_upcoming_expenses_returns_near_term_pressure() -> None:
    tools = DemoFinancialTools()

    result = tools.upcoming_expenses(UpcomingExpensesInput(user_id="user_123"))

    assert result.current_balance_minor == 250000
    assert result.upcoming_expenses_next_7_days_minor == 65000
    assert result.largest_upcoming_expense_minor == 45000
    assert result.days_until_next_expense == 2
    assert result.upcoming_expense_count == 3
    assert result.projected_balance_after_upcoming_minor == 185000
    assert result.available_buffer_until_salary_minor == 70000
    assert result.safe_to_spend_minor == 50000
    assert result.lookahead_days == 7
    assert result.days_until_salary == 9
    assert result.expected_expenses_high is True
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_purchase_simulation_uses_buffer_threshold() -> None:
    tools = DemoFinancialTools()

    result = tools.simulate_purchase(
        PurchaseSimulationInput(user_id="user_123", amount_minor=40000)
    )

    assert result.amount_minor == 40000
    assert result.safe_to_spend_minor == 50000
    assert result.buffer_after_purchase_minor == 30000
    assert result.days_until_salary == 9
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_installment_simulation_returns_monthly_payment_context() -> None:
    tools = DemoFinancialTools()

    result = tools.simulate_installments(
        InstallmentsSimulationInput(
            user_id="user_123",
            amount_minor=90000,
            months=3,
        )
    )

    assert result.amount_minor == 90000
    assert result.months == 3
    assert result.monthly_payment_minor == 30000
    assert result.safe_to_spend_minor == 50000
    assert result.buffer_after_monthly_payment_minor == 40000
    assert not hasattr(result, "answer")
    assert not hasattr(result, "risk_level")


def test_demo_installment_simulation_rounds_monthly_payment_up() -> None:
    tools = DemoFinancialTools()

    result = tools.simulate_installments(
        InstallmentsSimulationInput(
            user_id="user_123",
            amount_minor=10000,
            months=3,
        )
    )

    assert result.monthly_payment_minor == 3334
    assert result.buffer_after_monthly_payment_minor == 66666
