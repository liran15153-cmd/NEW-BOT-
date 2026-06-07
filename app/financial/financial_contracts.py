from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Currency(str, Enum):
    ILS = "ILS"


class CashflowStatusInput(BaseModel):
    user_id: str = Field(min_length=1)


class CashflowStatusResult(BaseModel):
    current_balance_minor: int
    committed_expenses_minor: int
    available_buffer_minor: int
    safe_to_spend_minor: int
    days_until_salary: int
    currency: Currency
    expected_expenses_high: bool


class WeeklySpendInput(BaseModel):
    user_id: str = Field(min_length=1)


class WeeklySpendResult(BaseModel):
    available_buffer_minor: int
    safe_to_spend_until_salary_minor: int
    daily_safe_to_spend_minor: int
    weekly_safe_to_spend_minor: int
    projected_buffer_after_weekly_spend_minor: int
    days_until_salary: int
    projection_days: int
    currency: Currency
    expected_expenses_high: bool


class OverdraftRiskInput(BaseModel):
    user_id: str = Field(min_length=1)


class OverdraftRiskResult(BaseModel):
    current_balance_minor: int
    committed_expenses_until_salary_minor: int
    projected_balance_before_salary_minor: int
    overdraft_gap_minor: int
    days_until_salary: int
    currency: Currency
    expected_expenses_high: bool


class PurchaseSimulationInput(BaseModel):
    user_id: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)
    currency: Currency = Currency.ILS


class PurchaseSimulationResult(BaseModel):
    amount_minor: int
    currency: Currency
    available_buffer_before_purchase_minor: int
    safe_to_spend_minor: int
    buffer_after_purchase_minor: int
    days_until_salary: int


class InstallmentsSimulationInput(BaseModel):
    user_id: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)
    months: int = Field(gt=0)
    currency: Currency = Currency.ILS


class InstallmentsSimulationResult(BaseModel):
    amount_minor: int
    months: int
    monthly_payment_minor: int
    currency: Currency
    available_buffer_before_payment_minor: int
    safe_to_spend_minor: int
    buffer_after_monthly_payment_minor: int
    days_until_salary: int


@runtime_checkable
class CashflowStatusTool(Protocol):
    def cashflow_status(self, request: CashflowStatusInput) -> CashflowStatusResult:
        ...


@runtime_checkable
class WeeklySpendTool(Protocol):
    def weekly_spend(self, request: WeeklySpendInput) -> WeeklySpendResult:
        ...


@runtime_checkable
class OverdraftRiskTool(Protocol):
    def overdraft_risk(self, request: OverdraftRiskInput) -> OverdraftRiskResult:
        ...


@runtime_checkable
class PurchaseSimulationTool(Protocol):
    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> PurchaseSimulationResult:
        ...


@runtime_checkable
class InstallmentsSimulationTool(Protocol):
    def simulate_installments(
        self,
        request: InstallmentsSimulationInput,
    ) -> InstallmentsSimulationResult:
        ...


@runtime_checkable
class FinancialTools(
    CashflowStatusTool,
    WeeklySpendTool,
    OverdraftRiskTool,
    PurchaseSimulationTool,
    InstallmentsSimulationTool,
    Protocol,
):
    pass

