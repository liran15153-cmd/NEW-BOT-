from dataclasses import dataclass

from app.financial.contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
    RiskLevel,
)


@dataclass(frozen=True)
class DemoFinancialContext:
    current_balance_minor: int = 250000
    committed_expenses_minor: int = 180000
    medium_buffer_threshold_minor: int = 100000
    days_until_salary: int = 9
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
            days_until_salary=self._context.days_until_salary,
            currency=self._context.currency,
            risk_level=_risk_for_remaining_buffer(
                self._context.available_buffer_minor,
                self._context.medium_buffer_threshold_minor,
            ),
        )

    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> PurchaseSimulationResult:
        available_buffer = self._context.available_buffer_minor
        remaining_buffer = available_buffer - request.amount_minor

        return PurchaseSimulationResult(
            amount_minor=request.amount_minor,
            currency=request.currency,
            available_buffer_before_purchase_minor=available_buffer,
            remaining_buffer_minor=remaining_buffer,
            can_purchase=remaining_buffer >= 0,
            risk_level=_risk_for_remaining_buffer(
                remaining_buffer,
                self._context.medium_buffer_threshold_minor,
            ),
        )

    def simulate_installments(
        self,
        request: InstallmentsSimulationInput,
    ) -> InstallmentsSimulationResult:
        monthly_payment_minor = request.amount_minor // request.months
        remaining_buffer = self._context.available_buffer_minor - monthly_payment_minor

        return InstallmentsSimulationResult(
            amount_minor=request.amount_minor,
            months=request.months,
            monthly_payment_minor=monthly_payment_minor,
            currency=request.currency,
            remaining_buffer_minor=remaining_buffer,
            risk_level=_risk_for_remaining_buffer(
                remaining_buffer,
                self._context.medium_buffer_threshold_minor,
            ),
        )


def _risk_for_remaining_buffer(
    remaining_buffer_minor: int,
    medium_buffer_threshold_minor: int,
) -> RiskLevel:
    if remaining_buffer_minor < 0:
        return RiskLevel.HIGH
    if remaining_buffer_minor < medium_buffer_threshold_minor:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
