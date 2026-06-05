from app.ai.schemas import IntentParseResult

_INSTALLMENT_KEYWORDS = (
    "אפרוס",
    "לפרוס",
    "פריסה",
    "תשלומים",
    "לתשלומים",
    "installment",
    "installments",
    "payments",
    "split",
    "months",
)
_PURCHASE_KEYWORDS = (
    "לקנות",
    "קנייה",
    "קניה",
    "רכישה",
    "אפשר לקנות",
    "buy",
    "purchase",
    "afford",
    "spend",
)
_CASHFLOW_KEYWORDS = (
    "תזרים",
    "יתרה",
    "תקציב",
    "מצב פיננסי",
    "cashflow",
    "cash flow",
    "balance",
    "budget",
    "buffer",
    "financial status",
)


def parse_intent(message: str) -> IntentParseResult:
    normalized = message.strip().casefold()

    if _contains_any(normalized, _INSTALLMENT_KEYWORDS):
        return IntentParseResult(
            intent="simulate_installments",
            confidence=0.8,
            matched_rule="installments_keyword",
            normalized_message=normalized,
        )

    if _contains_any(normalized, _PURCHASE_KEYWORDS):
        return IntentParseResult(
            intent="simulate_purchase",
            confidence=0.85,
            matched_rule="purchase_keyword",
            normalized_message=normalized,
        )

    if _contains_any(normalized, _CASHFLOW_KEYWORDS):
        return IntentParseResult(
            intent="cashflow_status",
            confidence=0.9,
            matched_rule="cashflow_keyword",
            normalized_message=normalized,
        )

    return IntentParseResult(
        intent="unknown",
        confidence=0.2,
        matched_rule=None,
        normalized_message=normalized,
    )


def _contains_any(message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in message for keyword in keywords)
