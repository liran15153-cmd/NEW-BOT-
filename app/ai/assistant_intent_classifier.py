from app.ai.assistant_policy_schemas import AssistantIntent
from app.ai.chat_message_schemas import IntentName

_SAFETY_BOUNDARY_KEYWORDS = (
    "ignore previous instructions",
    "ignore system",
    "system prompt",
    "developer message",
    "hidden prompt",
    "reveal secrets",
    "approve every purchase",
    "bypass safety",
    "show me your instructions",
    "\u05ea\u05ea\u05e2\u05dc\u05dd \u05de\u05d4\u05d4\u05d5\u05e8\u05d0\u05d5\u05ea",
    "\u05d4\u05ea\u05e2\u05dc\u05dd \u05de\u05d4\u05d4\u05d5\u05e8\u05d0\u05d5\u05ea",
    "\u05ea\u05d0\u05e9\u05e8 \u05db\u05dc \u05e7\u05e0\u05d9\u05d9\u05d4",
    "\u05d4\u05e0\u05d7\u05d9\u05d5\u05ea \u05de\u05e2\u05e8\u05db\u05ea",
    "\u05d4\u05d5\u05e8\u05d0\u05d5\u05ea \u05de\u05e1\u05ea\u05e8\u05d5\u05ea",
)
_TAX_OR_LEGAL_KEYWORDS = (
    "מס",
    "מיסים",
    "משפטי",
    "חוקי",
    "עורך דין",
    "tax",
    "legal",
    "lawyer",
)
_INVESTMENT_KEYWORDS = (
    "להשקיע",
    "השקעה",
    "מניה",
    "מניות",
    "קריפטו",
    "ביטקוין",
    "invest",
    "investment",
    "stock",
    "stocks",
    "crypto",
)
_LOAN_KEYWORDS = (
    "הלוואה",
    "לקחת הלוואה",
    "אשראי",
    "loan",
    "borrow",
    "credit",
)
_PRIVACY_KEYWORDS = (
    "מעסיק",
    "המעסיק",
    "רואה את זה",
    "פרטיות",
    "מי רואה",
    "employer",
    "privacy",
    "who can see",
)
_PAYMENT_SPLIT_KEYWORDS = (
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
_AFFORDABILITY_KEYWORDS = (
    "אפשר לקנות",
    "לקנות",
    "קנייה",
    "קניה",
    "רכישה",
    "buy",
    "purchase",
    "afford",
    "spend",
)
_CASHFLOW_KEYWORDS = (
    "תזרים",
    "יתרה",
    "יישאר",
    "ישאר",
    "נשאר",
    "משכורת",
    "תקציב",
    "מצב פיננסי",
    "cashflow",
    "cash flow",
    "balance",
    "budget",
    "buffer",
    "payday",
    "until payday",
)
_RECURRING_EXPENSE_KEYWORDS = (
    "מנוי",
    "מנויים",
    "הוראות קבע",
    "הוצאות קבועות",
    "subscriptions",
    "subscription",
    "recurring",
)
_MONEY_LEAK_KEYWORDS = (
    "נוזל לי כסף",
    "דליפה",
    "בזבוזים",
    "leak",
    "money leak",
    "waste",
)
_TRANSACTION_EXPLANATION_KEYWORDS = (
    "עסקה",
    "העסקה",
    "חיוב",
    "transaction",
    "charge",
)
_GENERAL_HELP_KEYWORDS = (
    "מה אתה יכול לעשות",
    "איך אתה יכול לעזור",
    "help",
    "what can you do",
)


def classify_assistant_intent(message: str) -> AssistantIntent:
    normalized = message.strip().casefold()

    ordered_rules: tuple[tuple[tuple[str, ...], AssistantIntent], ...] = (
        (_SAFETY_BOUNDARY_KEYWORDS, AssistantIntent.SAFETY_BOUNDARY_REQUEST),
        (_TAX_OR_LEGAL_KEYWORDS, AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE),
        (_INVESTMENT_KEYWORDS, AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE),
        (_LOAN_KEYWORDS, AssistantIntent.UNSUPPORTED_LOAN_ADVICE),
        (_PRIVACY_KEYWORDS, AssistantIntent.PRIVACY_QUESTION),
        (_PAYMENT_SPLIT_KEYWORDS, AssistantIntent.PAYMENT_SPLIT_SIMULATION),
        (_AFFORDABILITY_KEYWORDS, AssistantIntent.AFFORDABILITY_CHECK),
        (_CASHFLOW_KEYWORDS, AssistantIntent.CASHFLOW_STATUS),
        (_RECURRING_EXPENSE_KEYWORDS, AssistantIntent.RECURRING_EXPENSES),
        (_MONEY_LEAK_KEYWORDS, AssistantIntent.MONEY_LEAK_DETECTION),
        (_TRANSACTION_EXPLANATION_KEYWORDS, AssistantIntent.TRANSACTION_EXPLANATION),
        (_GENERAL_HELP_KEYWORDS, AssistantIntent.GENERAL_HELP),
    )
    for keywords, intent in ordered_rules:
        if _contains_any(normalized, keywords):
            return intent
    return AssistantIntent.UNKNOWN


def executable_intent_for(assistant_intent: AssistantIntent) -> IntentName | None:
    if assistant_intent == AssistantIntent.CASHFLOW_STATUS:
        return "cashflow_status"
    if assistant_intent == AssistantIntent.AFFORDABILITY_CHECK:
        return "simulate_purchase"
    if assistant_intent == AssistantIntent.PAYMENT_SPLIT_SIMULATION:
        return "simulate_installments"
    return None


def _contains_any(message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in message for keyword in keywords)
