from dataclasses import dataclass

from app.financial.financial_contracts import (
    CashflowStatusInput,
    CashflowStatusResult,
    Currency,
    InstallmentsSimulationInput,
    InstallmentsSimulationResult,
    PurchaseSimulationInput,
    PurchaseSimulationResult,
)


@dataclass(frozen=True)
class DemoFinancialContext:
    current_balance_minor: int = 250000
    committed_expenses_minor: int = 180000
    safe_to_spend_minor: int = 50000
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


