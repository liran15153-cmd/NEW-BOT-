from dataclasses import dataclass, field

from app.ai.chat_message_schemas import ExtractedParameters, IntentName
from app.financial.financial_contracts import (
    CashflowStatusInput,
    FinancialTools,
    InstallmentsSimulationInput,
    PurchaseSimulationInput,
    RiskLevel,
)
from app.financial.financial_decision_engine import DecisionResult, FinancialDecisionEngine
from app.financial.financial_reason_codes import ReasonCode


@dataclass(frozen=True)
class ToolExecutionResult:
    result: DecisionResult | None
    tool_called: str | None
    tool_executed: bool
    risk_level: RiskLevel | None
    reason_codes: list[ReasonCode] = field(default_factory=list)


def execute_tool(
    intent: IntentName,
    user_id: str,
    parameters: ExtractedParameters,
    tools: FinancialTools,
    decision_engine: FinancialDecisionEngine,
) -> ToolExecutionResult:
    if intent == "cashflow_status":
        facts = tools.cashflow_status(CashflowStatusInput(user_id=user_id))
        return _executed(
            "cashflow_status",
            decision_engine.decide_cashflow(facts),
        )

    if intent == "simulate_purchase":
        if parameters.amount_minor is None:
            raise ValueError("amount_minor is required before executing purchase tool.")
        facts = tools.simulate_purchase(
            PurchaseSimulationInput(
                user_id=user_id,
                amount_minor=parameters.amount_minor,
            )
        )
        return _executed(
            "simulate_purchase",
            decision_engine.decide_purchase(facts),
        )

    if intent == "simulate_installments":
        if parameters.amount_minor is None or parameters.months is None:
            raise ValueError(
                "amount_minor and months are required before executing installments tool."
            )
        facts = tools.simulate_installments(
            InstallmentsSimulationInput(
                user_id=user_id,
                amount_minor=parameters.amount_minor,
                months=parameters.months,
            )
        )
        return _executed(
            "simulate_installments",
            decision_engine.decide_installments(facts),
        )

    return ToolExecutionResult(
        result=None,
        tool_called=None,
        tool_executed=False,
        risk_level=None,
    )


def _executed(
    tool_called: str,
    result: DecisionResult,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        result=result,
        tool_called=tool_called,
        tool_executed=True,
        risk_level=result.risk_level,
        reason_codes=result.reason_codes,
    )


