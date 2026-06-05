from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class CashflowStatusInput(BaseModel):
    user_id: str = Field(min_length=1)


class PurchaseSimulationInput(BaseModel):
    user_id: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)


class InstallmentSimulationInput(BaseModel):
    user_id: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)
    installment_count: int = Field(gt=0)


class FinancialToolResult(BaseModel):
    answer: str
    tool_called: str


@runtime_checkable
class CashflowStatusTool(Protocol):
    def cashflow_status(self, request: CashflowStatusInput) -> FinancialToolResult:
        ...


@runtime_checkable
class PurchaseSimulationTool(Protocol):
    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> FinancialToolResult:
        ...


@runtime_checkable
class InstallmentSimulationTool(Protocol):
    def simulate_installments(
        self,
        request: InstallmentSimulationInput,
    ) -> FinancialToolResult:
        ...


@runtime_checkable
class FinancialTools(
    CashflowStatusTool,
    PurchaseSimulationTool,
    InstallmentSimulationTool,
    Protocol,
):
    pass
