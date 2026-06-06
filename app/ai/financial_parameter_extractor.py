from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from app.ai.chat_message_schemas import ExtractedParameters
from app.financial.financial_contracts import Currency

_AMOUNT_TEXT = r"\d[\d,]*(?:\.\d{1,2})?"
_ILS_SUFFIX = r"(?:שקל(?:ים)?|שח|ש\"ח|nis|ils|shekels?|₪)"
_MINUS_CHARS = "-\u2010\u2011\u2012\u2013\u2014\u2212"
_VALID_AMOUNT_PREFIX_BEFORE_MINUS = {"\u05d1", "\u05dc"}
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
            if _has_negative_amount_marker(message, match.start(1)):
                continue
            return _amount_text_to_minor(match.group(1))
    return None


def extract_months(message: str) -> int | None:
    for pattern in _MONTH_PATTERNS:
        match = pattern.search(message)
        if match:
            months = int(match.group(1))
            if months > 0:
                return months
            return None
    return None


def _amount_text_to_minor(amount_text: str) -> int | None:
    normalized = _normalize_amount_text(amount_text)
    try:
        amount = Decimal(normalized)
    except InvalidOperation:
        return None
    if amount <= 0:
        return None
    return int((amount * Decimal("100")).quantize(Decimal("1"), ROUND_HALF_UP))


def _normalize_amount_text(amount_text: str) -> str:
    if re.fullmatch(r"\d{1,3}(,\d{3})+(?:\.\d{1,2})?", amount_text):
        return amount_text.replace(",", "")
    return amount_text.replace(",", ".")


def _has_negative_amount_marker(message: str, amount_start: int) -> bool:
    previous_index = _previous_non_space_index(message, amount_start - 1)
    if previous_index is None:
        return False
    if message[previous_index] == "\u20aa":
        previous_index = _previous_non_space_index(message, previous_index - 1)
        if previous_index is None:
            return False
    if message[previous_index] not in _MINUS_CHARS:
        return False

    prefix_index = _previous_non_space_index(message, previous_index - 1)
    if prefix_index is None:
        return True
    return message[prefix_index] not in _VALID_AMOUNT_PREFIX_BEFORE_MINUS


def _previous_non_space_index(message: str, index: int) -> int | None:
    while index >= 0:
        if not message[index].isspace():
            return index
        index -= 1
    return None


