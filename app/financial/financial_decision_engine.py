from enum import Enum

from pydantic import BaseModel

from app.financial.financial_contracts import (
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationResult,
    OverdraftRiskResult,
    PurchaseSimulationResult,
    RiskLevel,
    UpcomingExpensesResult,
    WeeklySpendResult,
)
from app.financial.financial_reason_codes import ReasonCode


class RecommendedAction(str, Enum):
    PROCEED = "proceed"
    WAIT = "wait"
    REDUCE_AMOUNT = "reduce_amount"
    AVOID = "avoid"
    LIMIT_TO_SAFE_AMOUNT = "limit_to_safe_amount"
    REDUCE_SPENDING = "reduce_spending"


class CashflowDecisionResult(BaseModel):
    available_buffer_minor: int
    safe_to_spend_minor: int
    days_until_salary: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


class WeeklySpendDecisionResult(BaseModel):
    available_buffer_minor: int
    safe_to_spend_until_salary_minor: int
    daily_safe_to_spend_minor: int
    weekly_safe_to_spend_minor: int
    projected_buffer_after_weekly_spend_minor: int
    days_until_salary: int
    projection_days: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


class OverdraftRiskDecisionResult(BaseModel):
    will_enter_overdraft: bool
    current_balance_minor: int
    committed_expenses_until_salary_minor: int
    projected_balance_before_salary_minor: int
    overdraft_gap_minor: int
    days_until_salary: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


class UpcomingExpensesDecisionResult(BaseModel):
    current_balance_minor: int
    upcoming_expenses_next_7_days_minor: int
    largest_upcoming_expense_minor: int
    days_until_next_expense: int
    upcoming_expense_count: int
    projected_balance_after_upcoming_minor: int
    available_buffer_until_salary_minor: int
    safe_to_spend_minor: int
    lookahead_days: int
    days_until_salary: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


class PurchaseDecisionResult(BaseModel):
    can_purchase: bool
    amount_minor: int
    safe_to_spend_minor: int
    buffer_after_purchase_minor: int
    days_until_salary: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


class InstallmentsDecisionResult(BaseModel):
    amount_minor: int
    months: int
    monthly_payment_minor: int
    safe_to_spend_minor: int
    buffer_after_monthly_payment_minor: int
    days_until_salary: int
    currency: Currency
    risk_level: RiskLevel
    reason_codes: list[ReasonCode]
    recommended_action: RecommendedAction


DecisionResult = (
    CashflowDecisionResult
    | WeeklySpendDecisionResult
    | OverdraftRiskDecisionResult
    | UpcomingExpensesDecisionResult
    | PurchaseDecisionResult
    | InstallmentsDecisionResult
)


class FinancialDecisionEngine:
    def decide_cashflow(self, facts: CashflowStatusResult) -> CashflowDecisionResult:
        reason_codes: list[ReasonCode] = []
        if facts.available_buffer_minor >= facts.safe_to_spend_minor:
            reason_codes.append(ReasonCode.ENOUGH_BUFFER)
        else:
            reason_codes.append(ReasonCode.LOW_BUFFER_AFTER_PURCHASE)
        if facts.days_until_salary >= 7:
            reason_codes.append(ReasonCode.MANY_DAYS_UNTIL_SALARY)
        if facts.expected_expenses_high:
            reason_codes.append(ReasonCode.EXPECTED_EXPENSES_HIGH)

        risk_level = _risk_from_buffer(
            remaining_buffer_minor=facts.available_buffer_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            expected_expenses_high=facts.expected_expenses_high,
        )
        recommended_action = (
            RecommendedAction.WAIT
            if facts.expected_expenses_high or risk_level != RiskLevel.LOW
            else RecommendedAction.PROCEED
        )

        return CashflowDecisionResult(
            available_buffer_minor=facts.available_buffer_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            days_until_salary=facts.days_until_salary,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=recommended_action,
        )

    def decide_weekly_spend(
        self,
        facts: WeeklySpendResult,
    ) -> WeeklySpendDecisionResult:
        reason_codes: list[ReasonCode] = []
        if facts.weekly_safe_to_spend_minor > 0:
            reason_codes.append(ReasonCode.SAFE_WEEKLY_SPEND_AVAILABLE)
        else:
            reason_codes.append(ReasonCode.NO_SAFE_WEEKLY_SPEND)
        if facts.projection_days < facts.days_until_salary:
            reason_codes.append(ReasonCode.WEEKLY_SPEND_LIMITED_BY_PAYDAY_DISTANCE)
        if facts.days_until_salary >= 7:
            reason_codes.append(ReasonCode.MANY_DAYS_UNTIL_SALARY)
        if facts.expected_expenses_high:
            reason_codes.append(ReasonCode.EXPECTED_EXPENSES_HIGH)

        risk_level = _weekly_spend_risk(facts)
        return WeeklySpendDecisionResult(
            available_buffer_minor=facts.available_buffer_minor,
            safe_to_spend_until_salary_minor=facts.safe_to_spend_until_salary_minor,
            daily_safe_to_spend_minor=facts.daily_safe_to_spend_minor,
            weekly_safe_to_spend_minor=facts.weekly_safe_to_spend_minor,
            projected_buffer_after_weekly_spend_minor=(
                facts.projected_buffer_after_weekly_spend_minor
            ),
            days_until_salary=facts.days_until_salary,
            projection_days=facts.projection_days,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=_weekly_spend_action(
                weekly_safe_to_spend_minor=facts.weekly_safe_to_spend_minor,
                risk_level=risk_level,
            ),
        )

    def decide_overdraft_risk(
        self,
        facts: OverdraftRiskResult,
    ) -> OverdraftRiskDecisionResult:
        will_enter_overdraft = (
            facts.projected_balance_before_salary_minor < 0
            or facts.overdraft_gap_minor > 0
        )
        reason_codes = [
            ReasonCode.PROJECTED_OVERDRAFT
            if will_enter_overdraft
            else ReasonCode.NO_PROJECTED_OVERDRAFT
        ]
        if facts.days_until_salary >= 7:
            reason_codes.append(ReasonCode.MANY_DAYS_UNTIL_SALARY)
        if facts.expected_expenses_high:
            reason_codes.append(ReasonCode.EXPECTED_EXPENSES_HIGH)

        risk_level = _overdraft_risk_level(
            will_enter_overdraft=will_enter_overdraft,
            expected_expenses_high=facts.expected_expenses_high,
        )
        return OverdraftRiskDecisionResult(
            will_enter_overdraft=will_enter_overdraft,
            current_balance_minor=facts.current_balance_minor,
            committed_expenses_until_salary_minor=(
                facts.committed_expenses_until_salary_minor
            ),
            projected_balance_before_salary_minor=(
                facts.projected_balance_before_salary_minor
            ),
            overdraft_gap_minor=facts.overdraft_gap_minor,
            days_until_salary=facts.days_until_salary,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=_overdraft_action(risk_level),
        )

    def decide_upcoming_expenses(
        self,
        facts: UpcomingExpensesResult,
    ) -> UpcomingExpensesDecisionResult:
        reason_codes = _upcoming_expense_reason_codes(facts)
        risk_level = _upcoming_expense_risk(facts)
        return UpcomingExpensesDecisionResult(
            current_balance_minor=facts.current_balance_minor,
            upcoming_expenses_next_7_days_minor=(
                facts.upcoming_expenses_next_7_days_minor
            ),
            largest_upcoming_expense_minor=facts.largest_upcoming_expense_minor,
            days_until_next_expense=facts.days_until_next_expense,
            upcoming_expense_count=facts.upcoming_expense_count,
            projected_balance_after_upcoming_minor=(
                facts.projected_balance_after_upcoming_minor
            ),
            available_buffer_until_salary_minor=(
                facts.available_buffer_until_salary_minor
            ),
            safe_to_spend_minor=facts.safe_to_spend_minor,
            lookahead_days=facts.lookahead_days,
            days_until_salary=facts.days_until_salary,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=_upcoming_expense_action(risk_level),
        )

    def decide_purchase(
        self,
        facts: PurchaseSimulationResult,
    ) -> PurchaseDecisionResult:
        reason_codes: list[ReasonCode] = []
        if facts.buffer_after_purchase_minor >= 0:
            reason_codes.append(ReasonCode.ENOUGH_BUFFER)
        if (
            facts.amount_minor > facts.safe_to_spend_minor
            or facts.buffer_after_purchase_minor < 0
        ):
            reason_codes.append(ReasonCode.PURCHASE_EXCEEDS_SAFE_TO_SPEND)
        elif facts.buffer_after_purchase_minor < facts.safe_to_spend_minor:
            reason_codes.append(ReasonCode.LOW_BUFFER_AFTER_PURCHASE)
        if facts.days_until_salary >= 7:
            reason_codes.append(ReasonCode.MANY_DAYS_UNTIL_SALARY)

        can_purchase = facts.buffer_after_purchase_minor >= 0
        risk_level = _risk_from_buffer(
            remaining_buffer_minor=facts.buffer_after_purchase_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            expected_expenses_high=False,
        )
        recommended_action = _purchase_action(
            can_purchase=can_purchase,
            amount_minor=facts.amount_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            risk_level=risk_level,
        )

        return PurchaseDecisionResult(
            can_purchase=can_purchase,
            amount_minor=facts.amount_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            buffer_after_purchase_minor=facts.buffer_after_purchase_minor,
            days_until_salary=facts.days_until_salary,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=recommended_action,
        )

    def decide_installments(
        self,
        facts: InstallmentsSimulationResult,
    ) -> InstallmentsDecisionResult:
        reason_codes: list[ReasonCode] = []
        if facts.buffer_after_monthly_payment_minor >= facts.safe_to_spend_minor:
            reason_codes.append(ReasonCode.ENOUGH_BUFFER)
        else:
            reason_codes.append(ReasonCode.LOW_BUFFER_AFTER_PURCHASE)
        if facts.days_until_salary >= 7:
            reason_codes.append(ReasonCode.MANY_DAYS_UNTIL_SALARY)

        risk_level = _risk_from_buffer(
            remaining_buffer_minor=facts.buffer_after_monthly_payment_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            expected_expenses_high=False,
        )

        return InstallmentsDecisionResult(
            amount_minor=facts.amount_minor,
            months=facts.months,
            monthly_payment_minor=facts.monthly_payment_minor,
            safe_to_spend_minor=facts.safe_to_spend_minor,
            buffer_after_monthly_payment_minor=facts.buffer_after_monthly_payment_minor,
            days_until_salary=facts.days_until_salary,
            currency=facts.currency,
            risk_level=risk_level,
            reason_codes=reason_codes,
            recommended_action=(
                RecommendedAction.PROCEED
                if risk_level == RiskLevel.LOW
                else RecommendedAction.WAIT
            ),
        )


def _risk_from_buffer(
    remaining_buffer_minor: int,
    safe_to_spend_minor: int,
    expected_expenses_high: bool,
) -> RiskLevel:
    if remaining_buffer_minor < 0:
        return RiskLevel.HIGH
    if remaining_buffer_minor < safe_to_spend_minor or expected_expenses_high:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _weekly_spend_risk(facts: WeeklySpendResult) -> RiskLevel:
    if (
        facts.weekly_safe_to_spend_minor <= 0
        or facts.projected_buffer_after_weekly_spend_minor < 0
    ):
        return RiskLevel.HIGH
    if (
        facts.expected_expenses_high
        or facts.projection_days < facts.days_until_salary
        or facts.available_buffer_minor < facts.safe_to_spend_until_salary_minor
    ):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _weekly_spend_action(
    *,
    weekly_safe_to_spend_minor: int,
    risk_level: RiskLevel,
) -> RecommendedAction:
    if weekly_safe_to_spend_minor <= 0 or risk_level == RiskLevel.HIGH:
        return RecommendedAction.WAIT
    if risk_level == RiskLevel.MEDIUM:
        return RecommendedAction.LIMIT_TO_SAFE_AMOUNT
    return RecommendedAction.PROCEED


def _overdraft_risk_level(
    *,
    will_enter_overdraft: bool,
    expected_expenses_high: bool,
) -> RiskLevel:
    if will_enter_overdraft:
        return RiskLevel.HIGH
    if expected_expenses_high:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _overdraft_action(risk_level: RiskLevel) -> RecommendedAction:
    if risk_level == RiskLevel.HIGH:
        return RecommendedAction.REDUCE_SPENDING
    if risk_level == RiskLevel.MEDIUM:
        return RecommendedAction.LIMIT_TO_SAFE_AMOUNT
    return RecommendedAction.PROCEED


def _upcoming_expense_reason_codes(
    facts: UpcomingExpensesResult,
) -> list[ReasonCode]:
    if facts.upcoming_expenses_next_7_days_minor <= 0:
        return [ReasonCode.NO_UPCOMING_EXPENSE_PRESSURE]

    reason_codes: list[ReasonCode] = []
    if facts.days_until_next_expense <= facts.lookahead_days:
        reason_codes.append(ReasonCode.UPCOMING_EXPENSES_DUE_SOON)
    if facts.projected_balance_after_upcoming_minor < 0:
        reason_codes.append(ReasonCode.PROJECTED_OVERDRAFT)
    elif facts.upcoming_expenses_next_7_days_minor > facts.safe_to_spend_minor:
        reason_codes.append(ReasonCode.UPCOMING_EXPENSES_EXCEED_SAFE_TO_SPEND)
    if (
        facts.expected_expenses_high
        and facts.projected_balance_after_upcoming_minor >= 0
    ):
        reason_codes.append(ReasonCode.EXPECTED_EXPENSES_HIGH)
    return reason_codes


def _upcoming_expense_risk(facts: UpcomingExpensesResult) -> RiskLevel:
    if facts.projected_balance_after_upcoming_minor < 0:
        return RiskLevel.HIGH
    if (
        facts.expected_expenses_high
        or facts.upcoming_expenses_next_7_days_minor > facts.safe_to_spend_minor
    ):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _upcoming_expense_action(risk_level: RiskLevel) -> RecommendedAction:
    if risk_level == RiskLevel.HIGH:
        return RecommendedAction.REDUCE_SPENDING
    if risk_level == RiskLevel.MEDIUM:
        return RecommendedAction.LIMIT_TO_SAFE_AMOUNT
    return RecommendedAction.PROCEED


def _purchase_action(
    can_purchase: bool,
    amount_minor: int,
    safe_to_spend_minor: int,
    risk_level: RiskLevel,
) -> RecommendedAction:
    if not can_purchase:
        return RecommendedAction.AVOID
    if amount_minor > safe_to_spend_minor:
        return RecommendedAction.REDUCE_AMOUNT
    if risk_level != RiskLevel.LOW:
        return RecommendedAction.WAIT
    return RecommendedAction.PROCEED
