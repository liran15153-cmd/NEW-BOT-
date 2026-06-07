from datetime import date, timedelta
from threading import RLock
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

UPCOMING_EXPENSE_LOOKAHEAD_DAYS = 7


class FinancialObligation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    label: str = Field(min_length=1, max_length=80)
    amount_minor: int = Field(gt=0)
    due_date: date
    currency: Currency = Currency.ILS


class FinancialProfileSnapshot(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1)
    as_of_date: date
    current_balance_minor: int
    next_salary_date: date
    safety_buffer_minor: int = Field(default=0, ge=0)
    committed_obligations: list[FinancialObligation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "FinancialProfileSnapshot":
        if self.next_salary_date < self.as_of_date:
            raise ValueError("next_salary_date cannot be before as_of_date.")
        past_due_labels = [
            obligation.label
            for obligation in self.committed_obligations
            if obligation.due_date < self.as_of_date
        ]
        if past_due_labels:
            raise ValueError(
                "committed_obligations cannot include due dates before as_of_date."
            )
        return self


class MissingFinancialDataError(Exception):
    def __init__(
        self,
        *,
        missing_fields: list[str] | None = None,
        reason: str = "missing_financial_data",
    ) -> None:
        self.missing_fields = missing_fields or ["financial_data"]
        self.reason = reason
        super().__init__(reason)


class FinancialProfileStore(Protocol):
    def save(self, profile: FinancialProfileSnapshot) -> None:
        ...

    def get(self, user_id: str) -> FinancialProfileSnapshot | None:
        ...


class InMemoryFinancialProfileStore:
    def __init__(self) -> None:
        self._profiles: dict[str, FinancialProfileSnapshot] = {}
        self._lock = RLock()

    def save(self, profile: FinancialProfileSnapshot) -> None:
        with self._lock:
            self._profiles[profile.user_id] = profile

    def get(self, user_id: str) -> FinancialProfileSnapshot | None:
        with self._lock:
            return self._profiles.get(user_id)


class UserFinancialTools:
    def __init__(self, store: FinancialProfileStore) -> None:
        self._store = store

    def cashflow_status(self, request: CashflowStatusInput) -> CashflowStatusResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        return CashflowStatusResult(
            current_balance_minor=profile.current_balance_minor,
            committed_expenses_minor=projection.committed_until_salary_minor,
            available_buffer_minor=projection.available_buffer_minor,
            safe_to_spend_minor=projection.safe_to_spend_minor,
            days_until_salary=projection.days_until_salary,
            currency=Currency.ILS,
            expected_expenses_high=projection.expected_expenses_high,
        )

    def weekly_spend(self, request: WeeklySpendInput) -> WeeklySpendResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        projection_days = _bounded_projection_days(projection.days_until_salary)
        weekly_safe_to_spend = _project_safe_spend_minor(
            safe_to_spend_minor=projection.safe_to_spend_minor,
            days_until_salary=projection.days_until_salary,
            projection_days=projection_days,
        )

        return WeeklySpendResult(
            available_buffer_minor=projection.available_buffer_minor,
            safe_to_spend_until_salary_minor=projection.safe_to_spend_minor,
            daily_safe_to_spend_minor=_daily_safe_spend_minor(
                projection.safe_to_spend_minor,
                projection.days_until_salary,
            ),
            weekly_safe_to_spend_minor=weekly_safe_to_spend,
            projected_buffer_after_weekly_spend_minor=(
                projection.available_buffer_minor - weekly_safe_to_spend
            ),
            days_until_salary=projection.days_until_salary,
            projection_days=projection_days,
            currency=Currency.ILS,
            expected_expenses_high=projection.expected_expenses_high,
        )

    def overdraft_risk(self, request: OverdraftRiskInput) -> OverdraftRiskResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        return OverdraftRiskResult(
            current_balance_minor=profile.current_balance_minor,
            committed_expenses_until_salary_minor=(
                projection.committed_until_salary_minor
            ),
            projected_balance_before_salary_minor=projection.available_buffer_minor,
            overdraft_gap_minor=max(0, -projection.available_buffer_minor),
            days_until_salary=projection.days_until_salary,
            currency=Currency.ILS,
            expected_expenses_high=projection.expected_expenses_high,
        )

    def upcoming_expenses(
        self,
        request: UpcomingExpensesInput,
    ) -> UpcomingExpensesResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        upcoming_obligations = _obligations_due_by(
            profile,
            profile.as_of_date + timedelta(days=UPCOMING_EXPENSE_LOOKAHEAD_DAYS),
        )
        upcoming_total = _sum_obligations(upcoming_obligations)
        projected_balance_after_upcoming = profile.current_balance_minor - upcoming_total

        return UpcomingExpensesResult(
            current_balance_minor=profile.current_balance_minor,
            upcoming_expenses_next_7_days_minor=upcoming_total,
            largest_upcoming_expense_minor=_largest_obligation(upcoming_obligations),
            days_until_next_expense=_days_until_next_obligation(
                profile,
                upcoming_obligations,
            ),
            upcoming_expense_count=len(upcoming_obligations),
            projected_balance_after_upcoming_minor=projected_balance_after_upcoming,
            available_buffer_until_salary_minor=projection.available_buffer_minor,
            safe_to_spend_minor=projection.safe_to_spend_minor,
            lookahead_days=UPCOMING_EXPENSE_LOOKAHEAD_DAYS,
            days_until_salary=projection.days_until_salary,
            currency=Currency.ILS,
            expected_expenses_high=projection.expected_expenses_high,
        )

    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> PurchaseSimulationResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        return PurchaseSimulationResult(
            amount_minor=request.amount_minor,
            currency=request.currency,
            available_buffer_before_purchase_minor=projection.available_buffer_minor,
            safe_to_spend_minor=projection.safe_to_spend_minor,
            buffer_after_purchase_minor=(
                projection.available_buffer_minor - request.amount_minor
            ),
            days_until_salary=projection.days_until_salary,
        )

    def simulate_installments(
        self,
        request: InstallmentsSimulationInput,
    ) -> InstallmentsSimulationResult:
        profile = self._require_profile(request.user_id)
        projection = _build_projection(profile)
        monthly_payment_minor = _ceil_divide_minor(request.amount_minor, request.months)
        return InstallmentsSimulationResult(
            amount_minor=request.amount_minor,
            months=request.months,
            monthly_payment_minor=monthly_payment_minor,
            currency=request.currency,
            available_buffer_before_payment_minor=projection.available_buffer_minor,
            safe_to_spend_minor=projection.safe_to_spend_minor,
            buffer_after_monthly_payment_minor=(
                projection.available_buffer_minor - monthly_payment_minor
            ),
            days_until_salary=projection.days_until_salary,
        )

    def financial_context_summary(self, user_id: str) -> dict[str, object] | None:
        profile = self._store.get(user_id)
        if profile is None:
            return None
        return financial_context_summary(profile)

    def _require_profile(self, user_id: str) -> FinancialProfileSnapshot:
        profile = self._store.get(user_id)
        if profile is None:
            raise MissingFinancialDataError(reason="no_financial_profile")
        return profile


class _Projection(BaseModel):
    committed_until_salary_minor: int
    available_buffer_minor: int
    safe_to_spend_minor: int
    days_until_salary: int
    expected_expenses_high: bool


def financial_context_summary(profile: FinancialProfileSnapshot) -> dict[str, object]:
    return {
        "current_balance_minor": profile.current_balance_minor,
        "has_current_balance": True,
        "next_salary_date": profile.next_salary_date.isoformat(),
        "has_salary_date": True,
        "has_transactions": False,
        "has_recurring_expenses": False,
        "has_upcoming_expenses": True,
        "has_imported_data": True,
        "has_live_bank_data": False,
    }


def _build_projection(profile: FinancialProfileSnapshot) -> _Projection:
    committed_until_salary = _sum_obligations(
        _obligations_due_by(profile, profile.next_salary_date)
    )
    available_buffer = profile.current_balance_minor - committed_until_salary
    safe_to_spend = max(0, available_buffer - profile.safety_buffer_minor)
    return _Projection(
        committed_until_salary_minor=committed_until_salary,
        available_buffer_minor=available_buffer,
        safe_to_spend_minor=safe_to_spend,
        days_until_salary=(profile.next_salary_date - profile.as_of_date).days,
        expected_expenses_high=_expected_expenses_high(
            current_balance_minor=profile.current_balance_minor,
            committed_expenses_minor=committed_until_salary,
        ),
    )


def _obligations_due_by(
    profile: FinancialProfileSnapshot,
    end_date: date,
) -> list[FinancialObligation]:
    return [
        obligation
        for obligation in profile.committed_obligations
        if profile.as_of_date <= obligation.due_date <= end_date
    ]


def _sum_obligations(obligations: list[FinancialObligation]) -> int:
    return sum(obligation.amount_minor for obligation in obligations)


def _largest_obligation(obligations: list[FinancialObligation]) -> int:
    if not obligations:
        return 0
    return max(obligation.amount_minor for obligation in obligations)


def _days_until_next_obligation(
    profile: FinancialProfileSnapshot,
    obligations: list[FinancialObligation],
) -> int:
    if not obligations:
        return 0
    next_due = min(obligation.due_date for obligation in obligations)
    return (next_due - profile.as_of_date).days


def _expected_expenses_high(
    *,
    current_balance_minor: int,
    committed_expenses_minor: int,
) -> bool:
    if committed_expenses_minor <= 0:
        return False
    if current_balance_minor <= 0:
        return True
    return committed_expenses_minor * 2 >= current_balance_minor


def _ceil_divide_minor(amount_minor: int, parts: int) -> int:
    return -(-amount_minor // parts)


def _bounded_projection_days(days_until_salary: int) -> int:
    if days_until_salary <= 0:
        return 0
    return min(UPCOMING_EXPENSE_LOOKAHEAD_DAYS, days_until_salary)


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
