from app.financial.financial_contracts import (
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationResult,
    PurchaseSimulationResult,
)
from app.financial.financial_decision_engine import FinancialDecisionEngine, RecommendedAction
from app.financial.financial_reason_codes import ReasonCode


def test_purchase_decision_returns_structured_reason_codes_and_action() -> None:
    decision = FinancialDecisionEngine().decide_purchase(
        PurchaseSimulationResult(
            amount_minor=40000,
            currency=Currency.ILS,
            available_buffer_before_purchase_minor=70000,
            safe_to_spend_minor=50000,
            buffer_after_purchase_minor=30000,
            days_until_salary=9,
        )
    )

    assert decision.can_purchase is True
    assert decision.amount_minor == 40000
    assert decision.safe_to_spend_minor == 50000
    assert decision.buffer_after_purchase_minor == 30000
    assert decision.reason_codes == [
        ReasonCode.ENOUGH_BUFFER,
        ReasonCode.LOW_BUFFER_AFTER_PURCHASE,
        ReasonCode.MANY_DAYS_UNTIL_SALARY,
    ]
    assert decision.recommended_action == RecommendedAction.WAIT
    assert "answer" not in type(decision).model_fields


def test_purchase_decision_avoids_purchase_that_exceeds_safe_to_spend() -> None:
    decision = FinancialDecisionEngine().decide_purchase(
        PurchaseSimulationResult(
            amount_minor=90000,
            currency=Currency.ILS,
            available_buffer_before_purchase_minor=70000,
            safe_to_spend_minor=50000,
            buffer_after_purchase_minor=-20000,
            days_until_salary=9,
        )
    )

    assert decision.can_purchase is False
    assert ReasonCode.PURCHASE_EXCEEDS_SAFE_TO_SPEND in decision.reason_codes
    assert decision.recommended_action == RecommendedAction.AVOID


def test_installments_decision_returns_monthly_payment_recommendation() -> None:
    decision = FinancialDecisionEngine().decide_installments(
        InstallmentsSimulationResult(
            amount_minor=90000,
            months=3,
            monthly_payment_minor=30000,
            currency=Currency.ILS,
            available_buffer_before_payment_minor=70000,
            safe_to_spend_minor=50000,
            buffer_after_monthly_payment_minor=40000,
            days_until_salary=9,
        )
    )

    assert decision.months == 3
    assert decision.monthly_payment_minor == 30000
    assert ReasonCode.LOW_BUFFER_AFTER_PURCHASE in decision.reason_codes
    assert decision.recommended_action == RecommendedAction.WAIT


def test_cashflow_decision_returns_structured_cashflow_context() -> None:
    decision = FinancialDecisionEngine().decide_cashflow(
        CashflowStatusResult(
            current_balance_minor=250000,
            committed_expenses_minor=180000,
            available_buffer_minor=70000,
            safe_to_spend_minor=50000,
            days_until_salary=9,
            currency=Currency.ILS,
            expected_expenses_high=True,
        )
    )

    assert decision.available_buffer_minor == 70000
    assert ReasonCode.EXPECTED_EXPENSES_HIGH in decision.reason_codes
    assert decision.recommended_action == RecommendedAction.WAIT


