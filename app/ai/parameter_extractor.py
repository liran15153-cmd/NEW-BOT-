from decimal import Decimal, ROUND_HALF_UP
import re

from app.ai.schemas import ExtractedParameters
from app.financial.contracts import Currency

_AMOUNT_TEXT = r"\d[\d,]*(?:\.\d{1,2})?"
_ILS_SUFFIX = r"(?:שקל(?:ים)?|שח|ש\"ח|nis|ils|shekels?|₪)"
_AMOUNT_PATTERNS = (
    re.compile(rf"₪\s*({_AMOUNT_TEXT})", re.IGNORECASE),
    re.compile(rf"({_AMOUNT_TEXT})\s*{_ILS_SUFFIX}", re.IGNORECASE),
)
_MONTH_PATTERNS = (
    re.compile(r"(?:ל|ב)[\-־]?\s*(\d{1,2})\s*תשלומים", re.IGNORECASE),
    re.compile(r"(\d{1,2})\s*תשלומים", re.IGNORECASE),
    re.compile(r"(?:over|for|in)\s+(\d{1,2})\s+months?", re.IGNORECASE),
)


def extract_parameters(message: str) -> ExtractedParameters:
    amount_minor = extract_amount_minor(message)
    return ExtractedParameters(
        amount_minor=amount_minor,
        currency=Currency.ILS if amount_minor is not None else None,
        months=extract_months(message),
    )


def extract_amount_minor(message: str) -> int | None:
    for pattern in _AMOUNT_PATTERNS:
        match = pattern.search(message)
        if match:
            return _amount_text_to_minor(match.group(1))
    return None


def extract_months(message: str) -> int | None:
    for pattern in _MONTH_PATTERNS:
        match = pattern.search(message)
        if match:
            return int(match.group(1))
    return None


def _amount_text_to_minor(amount_text: str) -> int:
    normalized = _normalize_amount_text(amount_text)
    amount = Decimal(normalized)
    return int((amount * Decimal("100")).quantize(Decimal("1"), ROUND_HALF_UP))


def _normalize_amount_text(amount_text: str) -> str:
    if re.fullmatch(r"\d{1,3}(,\d{3})+(?:\.\d{1,2})?", amount_text):
        return amount_text.replace(",", "")
    return amount_text.replace(",", ".")
