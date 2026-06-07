from app.ai.chat_message_schemas import IntentParseResult

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
_WEEKLY_SPEND_KEYWORDS = (
    "כמה אפשר להוציא השבוע",
    "מה אפשר להוציא השבוע",
    "להוציא השבוע",
    "תקציב שבועי",
    "safe spend this week",
    "safely spend this week",
    "weekly budget",
)
_OVERDRAFT_RISK_KEYWORDS = (
    "אכנס למינוס",
    "להיכנס למינוס",
    "עלול להיכנס למינוס",
    "סיכון למינוס",
    "מינוס לפני המשכורת",
    "אוברדרפט",
    "overdraft",
    "negative balance",
    "below zero",
)
_UPCOMING_EXPENSES_KEYWORDS = (
    "תשלומים קרובים",
    "הוצאות קרובות",
    "חיובים קרובים",
    "יורדות השבוע",
    "יורד בקרוב",
    "מה יורד",
    "upcoming payments",
    "upcoming expenses",
    "payments are coming soon",
    "coming soon",
)
_CASHFLOW_KEYWORDS = (
    "תזרים",
    "יתרה",
    "נשאר",
    "משכורת",
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

    if _contains_any(normalized, _UPCOMING_EXPENSES_KEYWORDS):
        return IntentParseResult(
            intent="upcoming_expenses",
            confidence=0.86,
            matched_rule="upcoming_expenses_keyword",
            normalized_message=normalized,
        )

    if _contains_any(normalized, _INSTALLMENT_KEYWORDS):
        return IntentParseResult(
            intent="simulate_installments",
            confidence=0.8,
            matched_rule="installments_keyword",
            normalized_message=normalized,
        )

    if _contains_any(normalized, _WEEKLY_SPEND_KEYWORDS):
        return IntentParseResult(
            intent="weekly_spend",
            confidence=0.88,
            matched_rule="weekly_spend_keyword",
            normalized_message=normalized,
        )

    if _contains_any(normalized, _OVERDRAFT_RISK_KEYWORDS):
        return IntentParseResult(
            intent="overdraft_risk",
            confidence=0.87,
            matched_rule="overdraft_risk_keyword",
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
