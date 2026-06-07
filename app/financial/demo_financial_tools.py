from dataclasses import dataclass

from app.financial.financial_contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    OverdraftRiskInput,
    OverdraftRiskResult,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
    UpcomingExpensesInput,
    UpcomingExpensesResult,
    WeeklySpendInput,
    WeeklySpendResult,
)


@dataclass(frozen=True)
class DemoFinancialContext:
    current_balance_minor: int = 250000
    committed_expenses_minor: int = 180000
    safe_to_spend_minor: int = 50000
    upcoming_expenses_next_7_days_minor: int = 65000
    largest_upcoming_expense_minor: int = 45000
    days_until_next_expense: int = 2
    upcoming_expense_count: int = 3
    upcoming_expense_lookahead_days: int = 7
    days_until_salary: int = 9
    expected_expenses_high: bool = True
    currency: Currency = Currency.ILS

    @property
    def available_buffer_minor(self) -> int:
        return self.current_balance_minor - self.committed_expenses_minor


class DemoFinancialTools:
    def __init__(self, context: DemoFinancialContext | None = None) -> None:
        self._context = context or DemoFinancialContext()

    def cashflow_status(self, request: CashflowStatusInput) -> CashflowStatusResult:
        return CashflowStatusResult(
            current_balance_minor=self._context.current_balance_minor,
            committed_expenses_minor=self._context.committed_expenses_minor,
            available_buffer_minor=self._context.available_buffer_minor,
            safe_to_spend_minor=self._context.safe_to_spend_minor,
            days_until_salary=self._context.days_until_salary,
            currency=self._context.currency,
            expected_expenses_high=self._context.expected_expenses_high,
        )

    def weekly_spend(self, request: WeeklySpendInput) -> WeeklySpendResult:
        projection_days = _bounded_projection_days(self._context.days_until_salary)
        weekly_safe_to_spend = _project_safe_spend_minor(
            safe_to_spend_minor=self._context.safe_to_spend_minor,
            days_until_salary=self._context.days_until_salary,
            projection_days=projection_days,
        )

        return WeeklySpendResult(
            available_buffer_minor=self._context.available_buffer_minor,
            safe_to_spend_until_salary_minor=self._context.safe_to_spend_minor,
            daily_safe_to_spend_minor=_daily_safe_spend_minor(
                self._context.safe_to_spend_minor,
                self._context.days_until_salary,
            ),
            weekly_safe_to_spend_minor=weekly_safe_to_spend,
            projected_buffer_after_weekly_spend_minor=(
                self._context.available_buffer_minor - weekly_safe_to_spend
            ),
            days_until_salary=self._context.days_until_salary,
            projection_days=projection_days,
            currency=self._context.currency,
            expected_expenses_high=self._context.expected_expenses_high,
        )

    def overdraft_risk(self, request: OverdraftRiskInput) -> OverdraftRiskResult:
        projected_balance = self._context.available_buffer_minor
        return OverdraftRiskResult(
            current_balance_minor=self._context.current_balance_minor,
            committed_expenses_until_salary_minor=(
                self._context.committed_expenses_minor
            ),
            projected_balance_before_salary_minor=projected_balance,
            overdraft_gap_minor=max(0, -projected_balance),
            days_until_salary=self._context.days_until_salary,
            currency=self._context.currency,
            expected_expenses_high=self._context.expected_expenses_high,
        )

    def upcoming_expenses(
        self,
        request: UpcomingExpensesInput,
    ) -> UpcomingExpensesResult:
        projected_balance = (
            self._context.current_balance_minor
            - self._context.upcoming_expenses_next_7_days_minor
        )
        return UpcomingExpensesResult(
            current_balance_minor=self._context.current_balance_minor,
            upcoming_expenses_next_7_days_minor=(
                self._context.upcoming_expenses_next_7_days_minor
            ),
            largest_upcoming_expense_minor=(
                self._context.largest_upcoming_expense_minor
            ),
            days_until_next_expense=self._context.days_until_next_expense,
            upcoming_expense_count=self._context.upcoming_expense_count,
            projected_balance_after_upcoming_minor=projected_balance,
            available_buffer_until_salary_minor=self._context.available_buffer_minor,
            safe_to_spend_minor=self._context.safe_to_spend_minor,
            lookahead_days=self._context.upcoming_expense_lookahead_days,
            days_until_salary=self._context.days_until_salary,
            currency=self._context.currency,
            expected_expenses_high=self._context.expected_expenses_high,
        )

    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> PurchaseSimulationResult:
        available_buffer = self._context.available_buffer_minor

        return PurchaseSimulationResult(
            amount_minor=request.amount_minor,
            currency=request.currency,
            available_buffer_before_purchase_minor=available_buffer,
            safe_to_spend_minor=self._context.safe_to_spend_minor,
            buffer_after_purchase_minor=available_buffer - request.amount_minor,
            days_until_salary=self._context.days_until_salary,
        )

    def simulate_installments(
        self,
        request: InstallmentsSimulationInput,
    ) -> InstallmentsSimulationResult:
        monthly_payment_minor = _ceil_divide_minor(request.amount_minor, request.months)
        available_buffer = self._context.available_buffer_minor

        return InstallmentsSimulationResult(
            amount_minor=request.amount_minor,
            months=request.months,
            monthly_payment_minor=monthly_payment_minor,
            currency=request.currency,
            available_buffer_before_payment_minor=available_buffer,
            safe_to_spend_minor=self._context.safe_to_spend_minor,
            buffer_after_monthly_payment_minor=available_buffer - monthly_payment_minor,
            days_until_salary=self._context.days_until_salary,
        )


def _ceil_divide_minor(amount_minor: int, parts: int) -> int:
    return -(-amount_minor // parts)


def _bounded_projection_days(days_until_salary: int) -> int:
    if days_until_salary <= 0:
        return 0
    return min(7, days_until_salary)


def _daily_safe_spend_minor(
    safe_to_spend_minor: int,
    days_until_salary: int,
) -> int:
    if safe_to_spend_minor <= 0 or days_until_salary <= 0:
        return 0
    return safe_to_spend_minor // days_until_salary


def _project_safe_spend_minor(
    *,
    safe_to_spend_minor: int,
    days_until_salary: int,
    projection_days: int,
) -> int:
    if safe_to_spend_minor <= 0 or days_until_salary <= 0 or projection_days <= 0:
        return 0
    return (safe_to_spend_minor * projection_days) // days_until_salary
