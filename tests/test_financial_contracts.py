from app.financial.contracts import (
    CashflowStatusInput,
    CashflowStatusTool,
    InstallmentSimulationInput,
    InstallmentSimulationTool,
    PurchaseSimulationInput,
    PurchaseSimulationTool,
)
from app.financial.mock_tools import DemoFinancialTools


def test_demo_tools_satisfy_financial_protocols() -> None:
    tools = DemoFinancialTools()

    assert isinstance(tools, CashflowStatusTool)
    assert isinstance(tools, PurchaseSimulationTool)
    assert isinstance(tools, InstallmentSimulationTool)


def test_demo_cashflow_status_returns_structured_result() -> None:
    tools = DemoFinancialTools()

    result = tools.cashflow_status(CashflowStatusInput(user_id="user_123"))

    assert result.tool_called == "cashflow_status"
    assert "demo financial context" in result.answer


def test_demo_purchase_simulation_uses_buffer_threshold() -> None:
    tools = DemoFinancialTools()

    result = tools.simulate_purchase(
        PurchaseSimulationInput(user_id="user_123", amount_minor=40000)
    )

    assert result.tool_called == "simulate_purchase"
    assert result.answer == (
        "Based on the demo financial context, this purchase is possible "
        "but would leave a low buffer until salary day."
    )


def test_demo_installment_simulation_returns_monthly_payment_context() -> None:
    tools = DemoFinancialTools()

    result = tools.simulate_installments(
        InstallmentSimulationInput(
            user_id="user_123",
            amount_minor=120000,
            installment_count=6,
        )
    )

    assert result.tool_called == "simulate_installments"
    assert "6 months" in result.answer
    assert "200.00 shekels" in result.answer
