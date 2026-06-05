from decimal import Decimal, ROUND_HALF_UP
import re

from app.ai.schemas import ChatMessageRequest, ChatMessageResponse
from app.financial.contracts import (
    CashflowStatusInput,
    FinancialTools,
    InstallmentSimulationInput,
    PurchaseSimulationInput,
)

_CURRENCY_AMOUNT_PATTERNS = (
    re.compile(r"\u20aa\s*(\d+(?:[\.,]\d{1,2})?)", re.IGNORECASE),
    re.compile(
        r"(\d+(?:[\.,]\d{1,2})?)\s*(?:shekels?|nis|ils|\u20aa)\b",
        re.IGNORECASE,
    ),
)
_NUMBER_RE = re.compile(r"\b\d+(?:[\.,]\d{1,2})?\b")
_INSTALLMENT_COUNT_RE = re.compile(
    r"(?:over|for|in)\s+(\d{1,2})\s+(?:months?|installments?|payments?)"
    r"|(\d{1,2})\s+(?:months?|installments?|payments?)",
    re.IGNORECASE,
)
_INSTALLMENT_UNIT_AFTER_NUMBER_RE = re.compile(
    r"^\s*(?:months?|installments?|payments?)\b",
    re.IGNORECASE,
)


def extract_amount_minor(message: str) -> int | None:
    for pattern in _CURRENCY_AMOUNT_PATTERNS:
        match = pattern.search(message)
        if match:
            return _amount_text_to_minor(match.group(1))

    for match in _NUMBER_RE.finditer(message):
        if _INSTALLMENT_UNIT_AFTER_NUMBER_RE.match(message[match.end() :]):
            continue
        return _amount_text_to_minor(match.group(0))

    return None


def extract_installment_count(message: str) -> int | None:
    match = _INSTALLMENT_COUNT_RE.search(message)
    if not match:
        return None

    count_text = match.group(1) or match.group(2)
    return int(count_text)


class ChatRouter:
    def __init__(self, tools: FinancialTools) -> None:
        self._tools = tools

    def route(self, request: ChatMessageRequest) -> ChatMessageResponse:
        message = request.message
        normalized = message.lower()

        if _is_installment_message(normalized):
            return self._handle_installments(request)

        if _is_purchase_message(normalized):
            return self._handle_purchase(request)

        if _is_cashflow_message(normalized):
            result = self._tools.cashflow_status(
                CashflowStatusInput(user_id=request.user_id)
            )
            return ChatMessageResponse(
                answer=result.answer,
                intent="cashflow_status",
                tool_called=result.tool_called,
                confidence=0.9,
                missing_fields=[],
            )

        return ChatMessageResponse(
            answer=(
                "I could not match this message to a supported demo financial "
                "intent yet."
            ),
            intent="unknown",
            tool_called="none",
            confidence=0.2,
            missing_fields=[],
        )

    def _handle_purchase(self, request: ChatMessageRequest) -> ChatMessageResponse:
        amount_minor = extract_amount_minor(request.message)
        if amount_minor is None:
            return ChatMessageResponse(
                answer=(
                    "I need an amount in shekels before I can simulate this "
                    "demo purchase."
                ),
                intent="simulate_purchase",
                tool_called="none",
                confidence=0.75,
                missing_fields=["amount"],
            )

        result = self._tools.simulate_purchase(
            PurchaseSimulationInput(
                user_id=request.user_id,
                amount_minor=amount_minor,
            )
        )
        return ChatMessageResponse(
            answer=result.answer,
            intent="simulate_purchase",
            tool_called=result.tool_called,
            confidence=0.85,
            missing_fields=[],
        )

    def _handle_installments(self, request: ChatMessageRequest) -> ChatMessageResponse:
        amount_minor = extract_amount_minor(request.message)
        installment_count = extract_installment_count(request.message)

        missing_fields: list[str] = []
        if amount_minor is None:
            missing_fields.append("amount")
        if installment_count is None:
            missing_fields.append("installment_count")

        if missing_fields:
            return ChatMessageResponse(
                answer=(
                    "I need an amount in shekels and an installment count "
                    "before I can simulate this demo installment plan."
                ),
                intent="simulate_installments",
                tool_called="none",
                confidence=0.7,
                missing_fields=missing_fields,
            )

        result = self._tools.simulate_installments(
            InstallmentSimulationInput(
                user_id=request.user_id,
                amount_minor=amount_minor,
                installment_count=installment_count,
            )
        )
        return ChatMessageResponse(
            answer=result.answer,
            intent="simulate_installments",
            tool_called=result.tool_called,
            confidence=0.8,
            missing_fields=[],
        )


def _amount_text_to_minor(amount_text: str) -> int:
    amount = Decimal(amount_text.replace(",", "."))
    return int((amount * Decimal("100")).quantize(Decimal("1"), ROUND_HALF_UP))


def _is_cashflow_message(message: str) -> bool:
    return any(
        keyword in message
        for keyword in (
            "cashflow",
            "cash flow",
            "balance",
            "budget",
            "buffer",
            "financial status",
        )
    )


def _is_purchase_message(message: str) -> bool:
    return any(
        keyword in message
        for keyword in (
            "buy",
            "purchase",
            "afford",
            "spend",
        )
    )


def _is_installment_message(message: str) -> bool:
    return any(
        keyword in message
        for keyword in (
            "installment",
            "installments",
            "payment",
            "payments",
            "split",
            "months",
        )
    )
