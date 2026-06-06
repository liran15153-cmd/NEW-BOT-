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
    PurchaseSimulationTool,
    InstallmentsSimulationTool,
    Protocol,
):
    pass


