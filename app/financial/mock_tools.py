from dataclasses import dataclass

from app.financial.contracts import (
    CashflowStatusInput,
    FinancialToolResult,
    InstallmentSimulationInput,
    PurchaseSimulationInput,
)


@dataclass(frozen=True)
class DemoFinancialContext:
    current_balance_minor: int = 250000
    committed_expenses_minor: int = 180000
    low_buffer_threshold_minor: int = 50000
    days_until_salary: int = 9

    @property
    def available_buffer_minor(self) -> int:
        return self.current_balance_minor - self.committed_expenses_minor


class DemoFinancialTools:
    def __init__(self, context: DemoFinancialContext | None = None) -> None:
        self._context = context or DemoFinancialContext()

    def cashflow_status(self, request: CashflowStatusInput) -> FinancialToolResult:
        return FinancialToolResult(
            answer=(
                "Based on the demo financial context, you have "
                f"{_format_minor(self._context.available_buffer_minor)} available "
                "after committed expenses and "
                f"{self._context.days_until_salary} days until salary day."
            ),
            tool_called="cashflow_status",
        )

    def simulate_purchase(
        self,
        request: PurchaseSimulationInput,
    ) -> FinancialToolResult:
        remaining_buffer = self._context.available_buffer_minor - request.amount_minor

        if remaining_buffer >= self._context.low_buffer_threshold_minor:
            answer = (
                "Based on the demo financial context, this purchase looks safe "
                "and keeps a reasonable buffer until salary day."
            )
        elif remaining_buffer >= 0:
            answer = (
                "Based on the demo financial context, this purchase is possible "
                "but would leave a low buffer until salary day."
            )
        else:
            answer = (
                "Based on the demo financial context, this purchase is not "
                "recommended because it would exceed the available buffer before "
                "salary day."
            )

        return FinancialToolResult(
            answer=answer,
            tool_called="simulate_purchase",
        )

    def simulate_installments(
        self,
        request: InstallmentSimulationInput,
    ) -> FinancialToolResult:
        monthly_payment_minor = request.amount_minor // request.installment_count

        return FinancialToolResult(
            answer=(
                "Based on the demo financial context, splitting this purchase "
                f"over {request.installment_count} months would create a monthly "
                f"payment of {_format_minor(monthly_payment_minor)} and stays "
                "within the demo buffer."
            ),
            tool_called="simulate_installments",
        )


def _format_minor(amount_minor: int) -> str:
    shekels = amount_minor / 100
    return f"{shekels:.2f} shekels"
