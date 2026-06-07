from app.financial.financial_contracts import (
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationResult,
    OverdraftRiskResult,
    PurchaseSimulationResult,
    WeeklySpendResult,
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


def test_weekly_spend_decision_returns_structured_projection() -> None:
    decision = FinancialDecisionEngine().decide_weekly_spend(
        WeeklySpendResult(
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
    )

    assert decision.weekly_safe_to_spend_minor == 38888
    assert decision.daily_safe_to_spend_minor == 5555
    assert decision.projected_buffer_after_weekly_spend_minor == 31112
    assert decision.projection_days == 7
    assert decision.risk_level == "medium"
    assert decision.reason_codes == [
        ReasonCode.SAFE_WEEKLY_SPEND_AVAILABLE,
        ReasonCode.WEEKLY_SPEND_LIMITED_BY_PAYDAY_DISTANCE,
        ReasonCode.MANY_DAYS_UNTIL_SALARY,
        ReasonCode.EXPECTED_EXPENSES_HIGH,
    ]
    assert decision.recommended_action == RecommendedAction.LIMIT_TO_SAFE_AMOUNT
    assert "answer" not in type(decision).model_fields


def test_weekly_spend_decision_handles_no_safe_amount_as_high_risk() -> None:
    decision = FinancialDecisionEngine().decide_weekly_spend(
        WeeklySpendResult(
            available_buffer_minor=15000,
            safe_to_spend_until_salary_minor=0,
            daily_safe_to_spend_minor=0,
            weekly_safe_to_spend_minor=0,
            projected_buffer_after_weekly_spend_minor=15000,
            days_until_salary=5,
            projection_days=5,
            currency=Currency.ILS,
            expected_expenses_high=False,
        )
    )

    assert decision.risk_level == "high"
    assert decision.reason_codes == [ReasonCode.NO_SAFE_WEEKLY_SPEND]
    assert decision.recommended_action == RecommendedAction.WAIT


def test_overdraft_risk_decision_flags_demo_projection_as_medium_risk() -> None:
    decision = FinancialDecisionEngine().decide_overdraft_risk(
        OverdraftRiskResult(
            current_balance_minor=250000,
            committed_expenses_until_salary_minor=180000,
            projected_balance_before_salary_minor=70000,
            overdraft_gap_minor=0,
            days_until_salary=9,
            currency=Currency.ILS,
            expected_expenses_high=True,
        )
    )

    assert decision.will_enter_overdraft is False
    assert decision.projected_balance_before_salary_minor == 70000
    assert decision.overdraft_gap_minor == 0
    assert decision.risk_level == "medium"
    assert decision.reason_codes == [
        ReasonCode.NO_PROJECTED_OVERDRAFT,
        ReasonCode.MANY_DAYS_UNTIL_SALARY,
        ReasonCode.EXPECTED_EXPENSES_HIGH,
    ]
    assert decision.recommended_action == RecommendedAction.LIMIT_TO_SAFE_AMOUNT
    assert "answer" not in type(decision).model_fields


def test_overdraft_risk_decision_reduces_spending_when_projection_is_negative() -> None:
    decision = FinancialDecisionEngine().decide_overdraft_risk(
        OverdraftRiskResult(
            current_balance_minor=10000,
            committed_expenses_until_salary_minor=12500,
            projected_balance_before_salary_minor=-2500,
            overdraft_gap_minor=2500,
            days_until_salary=4,
            currency=Currency.ILS,
            expected_expenses_high=False,
        )
    )

    assert decision.will_enter_overdraft is True
    assert decision.overdraft_gap_minor == 2500
    assert decision.risk_level == "high"
    assert decision.reason_codes == [ReasonCode.PROJECTED_OVERDRAFT]
    assert decision.recommended_action == RecommendedAction.REDUCE_SPENDING

