from app.ai.chat_message_schemas import (
    ChatDebugInfo,
    ChatMessageResponse,
    ExtractedParameters,
    IntentName,
    IntentParseResult,
)
from app.ai.assistant_policy_schemas import (
    AnswerPlan,
    AssistantIntent,
    ResponsePolicyDecision,
    ResponseType,
)
from app.ai.financial_tool_executor import ToolExecutionResult
from app.financial.financial_decision_engine import (
    CashflowDecisionResult,
    InstallmentsDecisionResult,
    OverdraftRiskDecisionResult,
    PurchaseDecisionResult,
    WeeklySpendDecisionResult,
)
from app.financial.financial_reason_codes import ReasonCode


def build_unknown_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    *,
    session_id: str,
    assistant_intent: AssistantIntent | None = None,
    policy_decision: ResponsePolicyDecision | None = None,
    active_intent_before: IntentName | None = None,
    active_intent_after: IntentName | None = None,
    state_continued: bool = False,
    state_cleared: bool = False,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer=(
            "לא הצלחתי לזהות בקשה פיננסית נתמכת מתוך ההודעה הזו. "
            "אפשר לשאול על תזרים, קנייה נקודתית או פריסה לתשלומים."
        ),
        intent="unknown",
        status="unknown",
        tool_called=None,
        confidence=0.2,
        missing_fields=[],
        debug=_debug(
            intent_result,
            parameters,
            session_id=session_id,
            active_intent_before=active_intent_before,
            active_intent_after=active_intent_after,
            state_continued=state_continued,
            state_cleared=state_cleared,
            tool_executed=False,
            execution=None,
            assistant_intent=assistant_intent,
            policy_decision=policy_decision,
        ),
    )


def build_policy_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    *,
    assistant_intent: AssistantIntent,
    policy_decision: ResponsePolicyDecision,
    answer_plan: AnswerPlan,
    session_id: str,
    active_intent_before: IntentName | None = None,
    state_cleared: bool = False,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer=_policy_answer(assistant_intent, policy_decision, answer_plan),
        intent=assistant_intent.value,
        status=_policy_status(policy_decision.response_type),
        tool_called=None,
        confidence=0.8,
        missing_fields=answer_plan.missing_fields,
        debug=_debug(
            intent_result,
            parameters,
            session_id=session_id,
            active_intent_before=active_intent_before,
            active_intent_after=None,
            state_continued=False,
            state_cleared=state_cleared,
            tool_executed=False,
            execution=None,
            assistant_intent=assistant_intent,
            policy_decision=policy_decision,
        ),
    )


def build_missing_info_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    missing_fields: list[str],
    *,
    session_id: str,
    assistant_intent: AssistantIntent | None = None,
    policy_decision: ResponsePolicyDecision | None = None,
    active_intent_before: IntentName | None = None,
    active_intent_after: IntentName | None = None,
    state_continued: bool = False,
    state_cleared: bool = False,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer=_missing_info_answer(intent_result.intent, missing_fields),
        intent=intent_result.intent,
        status="needs_more_info",
        tool_called=None,
        confidence=_missing_info_confidence(intent_result.intent),
        missing_fields=missing_fields,
        debug=_debug(
            intent_result,
            parameters,
            session_id=session_id,
            active_intent_before=active_intent_before,
            active_intent_after=active_intent_after,
            state_continued=state_continued,
            state_cleared=state_cleared,
            tool_executed=False,
            execution=None,
            assistant_intent=assistant_intent,
            policy_decision=policy_decision,
        ),
    )


def build_answered_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    execution: ToolExecutionResult,
    *,
    session_id: str,
    assistant_intent: AssistantIntent | None = None,
    policy_decision: ResponsePolicyDecision | None = None,
    active_intent_before: IntentName | None = None,
    active_intent_after: IntentName | None = None,
    state_continued: bool = False,
    state_cleared: bool = False,
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
            session_id=session_id,
            active_intent_before=active_intent_before,
            active_intent_after=active_intent_after,
            state_continued=state_continued,
            state_cleared=state_cleared,
            tool_executed=execution.tool_executed,
            execution=execution,
            assistant_intent=assistant_intent,
            policy_decision=policy_decision,
        ),
    )


def build_error_response(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    *,
    session_id: str,
) -> ChatMessageResponse:
    return ChatMessageResponse(
        answer="אירעה שגיאה פנימית בבדיקת ההודעה. נסה שוב בעוד רגע.",
        intent=intent_result.intent,
        status="error",
        tool_called=None,
        confidence=intent_result.confidence,
        missing_fields=[],
        debug=_debug(
            intent_result,
            parameters,
            session_id=session_id,
            active_intent_before=None,
            active_intent_after=None,
            state_continued=False,
            state_cleared=False,
            tool_executed=False,
            execution=None,
        ),
    )


def _debug(
    intent_result: IntentParseResult,
    parameters: ExtractedParameters,
    *,
    session_id: str,
    active_intent_before: IntentName | None,
    active_intent_after: IntentName | None,
    state_continued: bool,
    state_cleared: bool,
    tool_executed: bool,
    execution: ToolExecutionResult | None,
    assistant_intent: AssistantIntent | None = None,
    policy_decision: ResponsePolicyDecision | None = None,
) -> ChatDebugInfo:
    return ChatDebugInfo(
        session_id=session_id,
        normalized_message=intent_result.normalized_message,
        matched_rule=intent_result.matched_rule,
        parameters=parameters,
        assistant_intent=assistant_intent,
        response_type=(
            policy_decision.response_type if policy_decision is not None else None
        ),
        policy_allowed=policy_decision.allowed if policy_decision is not None else None,
        policy_reason=policy_decision.reason if policy_decision is not None else None,
        blocked_reason=(
            policy_decision.blocked_reason if policy_decision is not None else None
        ),
        data_readiness_level=(
            policy_decision.data_readiness.level
            if policy_decision is not None and policy_decision.data_readiness is not None
            else None
        ),
        required_disclaimers=(
            policy_decision.required_disclaimers
            if policy_decision is not None
            else []
        ),
        active_intent_before=active_intent_before,
        active_intent_after=active_intent_after,
        state_continued=state_continued,
        state_cleared=state_cleared,
        tool_executed=tool_executed,
        risk_level=execution.risk_level if execution is not None else None,
        reason_codes=execution.reason_codes if execution is not None else [],
    )


def _policy_status(response_type: ResponseType):
    if response_type in {
        ResponseType.ASK_FOR_MISSING_DATA,
        ResponseType.CLARIFYING_QUESTION,
    }:
        return "needs_more_info"
    if response_type == ResponseType.ERROR_FALLBACK:
        return "error"
    return "answered"


def _policy_answer(
    assistant_intent: AssistantIntent,
    policy_decision: ResponsePolicyDecision,
    answer_plan: AnswerPlan,
) -> str:
    if assistant_intent == AssistantIntent.UNSUPPORTED_LOAN_ADVICE:
        return (
            "אני לא יכול להמליץ לקחת הלוואה. אני כן יכול לעזור לבדוק "
            "איך סכום מסוים ישפיע על התזרים שלך."
        )
    if assistant_intent == AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE:
        return (
            "אני לא יכול לתת המלצת השקעה. אני כן יכול לעזור לבדוק "
            "איך סכום מסוים ישפיע על התזרים שלך."
        )
    if assistant_intent == AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE:
        return (
            "אני לא יכול לתת ייעוץ מס או ייעוץ משפטי. לשאלה כזו כדאי "
            "לפנות לאיש מקצוע מתאים."
        )
    if assistant_intent == AssistantIntent.SAFETY_BOUNDARY_REQUEST:
        return (
            "אני לא יכול לעקוף הוראות בטיחות או פרטיות. אפשר לשאול אותי "
            "על תזרים, קנייה נקודתית או פריסה לתשלומים לפי נתוני הדמו."
        )
    if assistant_intent == AssistantIntent.PRIVACY_QUESTION:
        return (
            "בשלב הנוכחי אין במערכת שכבת מעסיק או נתונים אמיתיים. "
            "במוצר עתידי, המעסיק לא אמור לראות יתרות, עסקאות, שכר, "
            "חובות או שאלות אישיות."
        )
    if assistant_intent == AssistantIntent.RECURRING_EXPENSES:
        return (
            "כדי לזהות מנויים, צריך היסטוריית עסקאות. כרגע אין במערכת "
            "חיבור לעסקאות אמיתיות."
        )
    if assistant_intent == AssistantIntent.MONEY_LEAK_DETECTION:
        return (
            "כדי לזהות דליפות כסף, צריך היסטוריית עסקאות. כרגע אין "
            "במערכת חיבור לעסקאות אמיתיות."
        )
    if assistant_intent == AssistantIntent.TRANSACTION_EXPLANATION:
        return (
            "כדי להסביר עסקה מסוימת, צריך את פרטי העסקה והיסטוריית "
            "עסקאות. כרגע אין במערכת חיבור לעסקאות אמיתיות."
        )
    if answer_plan.main_message_key == "transaction_history_required":
        return (
            "כדי לזהות מנויים, דליפות כסף או חיובים חריגים, צריך היסטוריית "
            "עסקאות. כרגע אין במערכת חיבור לעסקאות אמיתיות."
        )
    if policy_decision.response_type == ResponseType.CLARIFYING_QUESTION:
        return "אני צריך עוד פרט אחד כדי לענות בצורה בטוחה."
    if policy_decision.response_type == ResponseType.ASK_FOR_MISSING_DATA:
        return "אין לי מספיק נתונים פיננסיים כדי לענות על זה בביטחון."
    if assistant_intent == AssistantIntent.GENERAL_HELP:
        return (
            "אפשר לשאול אותי על תזרים, קנייה נקודתית או פריסה לתשלומים "
            "על בסיס נתוני דמו."
        )
    return "אין לי מספיק מידע כדי לענות על זה בביטחון."


def _missing_info_answer(intent: str, missing_fields: list[str]) -> str:
    if intent == "simulate_purchase":
        return "על איזה סכום מדובר?"

    if "amount" in missing_fields and "months" in missing_fields:
        return "כדי לבדוק פריסה לתשלומים, אני צריך סכום ומספר חודשים."
    if "amount" in missing_fields:
        return "מה הסכום שתרצה לפרוס?"
    return "לכמה תשלומים או חודשים תרצה לפרוס?"


def _missing_info_confidence(intent: str) -> float:
    if intent == "simulate_purchase":
        return 0.75
    if intent == "simulate_installments":
        return 0.7
    return 0.2


def _answered_text(
    result: (
        CashflowDecisionResult
        | WeeklySpendDecisionResult
        | OverdraftRiskDecisionResult
        | PurchaseDecisionResult
        | InstallmentsDecisionResult
        | None
    ),
) -> str:
    if isinstance(result, CashflowDecisionResult):
        return (
            "לפי נתוני הדמו, נשארו לך "
            f"{_format_minor(result.available_buffer_minor)} פנויים, ומתוכם "
            f"{_format_minor(result.safe_to_spend_minor)} מוגדרים כסכום בטוח יחסית. "
            f"יש עוד {result.days_until_salary} ימים עד המשכורת. "
            f"רמת הסיכון: {_risk_label(result.risk_level)}."
        )

    if isinstance(result, WeeklySpendDecisionResult):
        if result.weekly_safe_to_spend_minor <= 0:
            return (
                "לפי נתוני הדמו, אין כרגע סכום בטוח להוצאה השבוע. "
                "עדיף לעצור הוצאות לא הכרחיות עד שתהיה תמונת תזרים ברורה יותר."
            )
        return (
            "לפי נתוני הדמו, הסכום הבטוח יחסית להוצאה השבוע הוא "
            f"{_format_minor(result.weekly_safe_to_spend_minor)}. "
            f"זה מחושב על בסיס {result.projection_days} ימים מתוך "
            f"{result.days_until_salary} ימים עד המשכורת, בערך "
            f"{_format_minor(result.daily_safe_to_spend_minor)} ליום. "
            f"רמת הסיכון: {_risk_label(result.risk_level)}."
        )

    if isinstance(result, OverdraftRiskDecisionResult):
        if result.will_enter_overdraft:
            return (
                "לפי נתוני הדמו, יש סיכון גבוה להיכנס למינוס לפני המשכורת. "
                "אחרי ההוצאות המחויבות צפוי פער של "
                f"{_format_minor(result.overdraft_gap_minor)}. "
                "עדיף לצמצם הוצאות לא הכרחיות עכשיו. "
                f"רמת הסיכון: {_risk_label(result.risk_level)}."
            )
        risk_note = (
            "בגלל שיש עוד "
            f"{result.days_until_salary} ימים עד המשכורת וההוצאות הצפויות גבוהות, "
            "כדאי להגביל הוצאות לסכום הבטוח. "
            if ReasonCode.EXPECTED_EXPENSES_HIGH in result.reason_codes
            else f"יש עוד {result.days_until_salary} ימים עד המשכורת. "
        )
        return (
            "לפי נתוני הדמו, לא צפויה כניסה למינוס לפני המשכורת. "
            "אחרי ההוצאות המחויבות צפויה להישאר יתרה של "
            f"{_format_minor(result.projected_balance_before_salary_minor)}. "
            f"{risk_note}"
            f"רמת הסיכון: {_risk_label(result.risk_level)}."
        )

    if isinstance(result, PurchaseDecisionResult):
        if not result.can_purchase:
            return (
                "לפי נתוני הדמו, לא מומלץ לבצע קנייה של "
                f"{_format_minor(result.amount_minor)} כרגע. "
                "היא חורגת מהסכום הבטוח ותפגע בכרית עד המשכורת."
            )
        if ReasonCode.LOW_BUFFER_AFTER_PURCHASE in result.reason_codes:
            return (
                "לפי נתוני הדמו, קנייה של "
                f"{_format_minor(result.amount_minor)} אפשרית, אבל היא תשאיר כרית "
                "ביטחון נמוכה עד המשכורת. עדיף להמתין או להפחית את הסכום."
            )
        return (
            "לפי נתוני הדמו, קנייה של "
            f"{_format_minor(result.amount_minor)} אפשרית והיא עדיין משאירה "
            "כרית ביטחון סבירה עד המשכורת."
        )

    if isinstance(result, InstallmentsDecisionResult):
        return (
            "לפי נתוני הדמו, פריסה ל-"
            f"{result.months} תשלומים תיצור תשלום חודשי של "
            f"{_format_minor(result.monthly_payment_minor)}. "
            "חשוב לזכור שפריסה יוצרת התחייבות עתידית. "
            f"רמת הסיכון: {_risk_label(result.risk_level)}."
        )

    return "לא הצלחתי לבנות תשובה פיננסית מהנתונים הקיימים."


def _format_minor(amount_minor: int) -> str:
    amount = amount_minor / 100
    if amount.is_integer():
        return f"{int(amount)} ₪"
    return f"{amount:.2f} ₪"


def _risk_label(risk_level) -> str:
    if risk_level == "low":
        return "נמוכה"
    if risk_level == "medium":
        return "בינונית"
    return "גבוהה"
