from dataclasses import dataclass

from app.ai.schemas import ExtractedParameters, IntentName
from app.financial.contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    FinancialTools,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
    RiskLevel,
)

FinancialExecutionResult = (
    CashflowStatusResult | PurchaseSimulationResult | InstallmentsSimulationResult
)


@dataclass(frozen=True)
class ToolExecutionResult:
    result: FinancialExecutionResult | None
    tool_called: str | None
    tool_executed: bool
    risk_level: RiskLevel | None


def execute_tool(
    intent: IntentName,
    user_id: str,
    parameters: ExtractedParameters,
    tools: FinancialTools,
) -> ToolExecutionResult:
    if intent == "cashflow_status":
        result = tools.cashflow_status(CashflowStatusInput(user_id=user_id))
        return _executed("cashflow_status", result)

    if intent == "simulate_purchase":
        if parameters.amount_minor is None:
            raise ValueError("amount_minor is required before executing purchase tool.")
        result = tools.simulate_purchase(
            PurchaseSimulationInput(
                user_id=user_id,
                amount_minor=parameters.amount_minor,
            )
        )
        return _executed("simulate_purchase", result)

    if intent == "simulate_installments":
        if parameters.amount_minor is None or parameters.months is None:
            raise ValueError(
                "amount_minor and months are required before executing installments tool."
            )
        result = tools.simulate_installments(
            InstallmentsSimulationInput(
                user_id=user_id,
                amount_minor=parameters.amount_minor,
                months=parameters.months,
            )
        )
        return _executed("simulate_installments", result)

    return ToolExecutionResult(
        result=None,
        tool_called=None,
        tool_executed=False,
        risk_level=None,
    )


def _executed(
    tool_called: str,
    result: FinancialExecutionResult,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        result=result,
        tool_called=tool_called,
        tool_executed=True,
        risk_level=result.risk_level,
    )
