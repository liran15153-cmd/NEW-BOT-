from app.ai.schemas import (
    ChatDebugInfo,
    ChatMessageResponse,
    ExtractedParameters,
    IntentParseResult,
)
from app.ai.tool_executor import ToolExecutionResult
from app.financial.contracts import (
    CashflowStatusResult,
    InstallmentsSimulationResult,
    PurchaseSimulationResult,
    RiskLevel,
)


def build_unknown_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer="לא הצלחתי לזהות בקשה פיננסית נתמכת מתוך ההודעה הזו.",
        intent="unknown",
        status="unknown",
        tool_called=None,
        confidence=0.2,
        missing_fields=[],
        debug=_debug(intent_result, parameters, False, None),
    )


def build_missing_info_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    missing_fields: list[str],
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer=_missing_info_answer(intent_result.intent, missing_fields),
        intent=intent_result.intent,
        status="needs_more_info",
        tool_called=None,
        confidence=_missing_info_confidence(intent_result.intent),
        missing_fields=missing_fields,
        debug=_debug(intent_result, parameters, False, None),
    )


def build_answered_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    execution: ToolExecutionResult,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer=_answered_text(execution.result),
        intent=intent_result.intent,
        status="answered",
        tool_called=execution.tool_called,
        confidence=intent_result.confidence,
        missing_fields=[],
        debug=_debug(
            intent_result,
            parameters,
            execution.tool_executed,
            execution.risk_level,
        ),
    )


def build_error_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer="אירעה שגיאה פנימית בבדיקת ההודעה. נסה שוב בעוד רגע.",
        intent=intent_result.intent,
        status="error",
        tool_called=None,
        confidence=intent_result.confidence,
        missing_fields=[],
        debug=_debug(intent_result, parameters, False, None),
    )


def _debug(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    tool_executed: bool,
    risk_level: RiskLevel | None,
) -> ChatDebugInfo:
    return ChatDebugInfo(
        normalized_message=intent_result.normalized_message,
        matched_rule=intent_result.matched_rule,
        parameters=parameters,
        tool_executed=tool_executed,
        risk_level=risk_level,
    )


def _missing_info_answer(intent: str, missing_fields: list[str]) -> str:
    if intent == "simulate_purchase":
        return "כדי לבדוק אם אפשר לבצע את הקנייה, אני צריך סכום בשקלים."

    if "amount" in missing_fields and "months" in missing_fields:
        return "כדי לבדוק פריסה לתשלומים, אני צריך סכום ומספר חודשים."
    if "amount" in missing_fields:
        return "כדי לבדוק פריסה לתשלומים, אני צריך סכום בשקלים."
    return "כדי לבדוק פריסה לתשלומים, אני צריך לדעת לכמה חודשים לפרוס."


def _missing_info_confidence(intent: str) -> float:
    if intent == "simulate_purchase":
        return 0.75
    if intent == "simulate_installments":
        return 0.7
    return 0.2


def _answered_text(
    result: CashflowStatusResult | PurchaseSimulationResult | InstallmentsSimulationResult | None,
) -> str:
    if isinstance(result, CashflowStatusResult):
        return (
            "לפי נתוני הדמו, נשארו לך "
            f"{_format_minor(result.available_buffer_minor)} פנויים אחרי הוצאות "
            f"מחויבות, ויש עוד {result.days_until_salary} ימים עד המשכורת. "
            f"רמת הסיכון: {_risk_label(result.risk_level)}."
        )

    if isinstance(result, PurchaseSimulationResult):
        if not result.can_purchase:
            return (
                "לפי נתוני הדמו, לא מומלץ לבצע את הקנייה הזו כרגע כי היא "
                "תחרוג מהכרית הפנויה לפני המשכורת."
            )
        if result.risk_level == RiskLevel.LOW:
            return (
                "לפי נתוני הדמו, אפשר לבצע את הקנייה והיא עדיין משאירה "
                "כרית ביטחון סבירה עד המשכורת."
            )
        return (
            "לפי נתוני הדמו, אפשר לבצע את הקנייה, אבל היא תשאיר כרית "
            "ביטחון נמוכה עד המשכורת."
        )

    if isinstance(result, InstallmentsSimulationResult):
        return (
            "לפי נתוני הדמו, פריסה ל-"
            f"{result.months} תשלומים תיצור תשלום חודשי של "
            f"{_format_minor(result.monthly_payment_minor)} ותשאיר רמת סיכון "
            f"{_risk_label(result.risk_level)}."
        )

    return "לא הצלחתי לבנות תשובה פיננסית מהנתונים הקיימים."


def _format_minor(amount_minor: int) -> str:
    amount = amount_minor / 100
    if amount.is_integer():
        return f"{int(amount)} ₪"
    return f"{amount:.2f} ₪"


def _risk_label(risk_level: RiskLevel) -> str:
    if risk_level == RiskLevel.LOW:
        return "נמוכה"
    if risk_level == RiskLevel.MEDIUM:
        return "בינונית"
    return "גבוהה"
