from app.financial.financial_contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    CashflowStatusTool,
    Currency,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    InstallmentsSimulationTool,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
    PurchaseSimulationTool,
)
from app.financial.demo_financial_tools import DemoFinancialTools


def test_demo_tools_satisfy_financial_protocols() -> None:
    tools = DemoFinancialTools()

    assert isinstance(tools, CashflowStatusTool)
    assert isinstance(tools, PurchaseSimulationTool)
    assert isinstance(tools, InstallmentsSimulationTool)


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

    assert "answer" not in CashflowStatusResult.model_fields
    assert "answer" not in PurchaseSimulationResult.model_fields
    assert "answer" not in InstallmentsSimulationResult.model_fields
    assert "risk_level" not in CashflowStatusResult.model_fields
    assert "risk_level" not in PurchaseSimulationResult.model_fields
    assert "risk_level" not in InstallmentsSimulationResult.model_fields
    assert cashflow.safe_to_spend_minor == 50000
    assert purchase.currency == Currency.ILS
    assert installments.months == 3


def test_demo_cashflow_status_returns_structured_result() -> None:
    tools = DemoFinancialTools()

    result = tools.cashflow_status(CashflowStatusInput(user_id="user_123"))

    assert result.available_buffer_minor == 70000
    assert result.safe_to_spend_minor == 50000
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


