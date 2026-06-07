from datetime import UTC, datetime

from app.ai.assistant_intent_classifier import (
    classify_assistant_intent,
    executable_intent_for,
)
from app.ai.assistant_answer_plan import build_answer_plan
from app.ai.assistant_policy_schemas import AssistantIntent
from app.ai.assistant_response_policy import decide_response_policy
from app.ai.financial_intent_parser import parse_intent
from app.ai.financial_parameter_extractor import extract_parameters
from app.ai.hebrew_response_builder import (
    build_answered_response,
    build_missing_info_response,
    build_policy_response,
    build_unknown_response,
)
from app.ai.chat_message_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ExtractedParameters,
    IntentName,
)
from app.ai.financial_tool_executor import execute_tool
from app.dialogue.conversation_flow_manager import DialogueManager, ResolvedDialogueTurn
from app.dialogue.conversation_state import ConversationState
from app.dialogue.conversation_state_store import ConversationStateStore
from app.financial.financial_contracts import FinancialTools
from app.financial.financial_decision_engine import FinancialDecisionEngine


class ChatRouter:
    def __init__(
        self,
        *,
        tools: FinancialTools,
        state_store: ConversationStateStore,
        decision_engine: FinancialDecisionEngine,
        dialogue_manager: DialogueManager | None = None,
    ) -> None:
        self._tools = tools
        self._state_store = state_store
        self._decision_engine = decision_engine
        self._dialogue_manager = dialogue_manager or DialogueManager()

    def route(self, request: ChatMessageRequest) -> ChatMessageResponse:
        session_id = _resolve_session_id(request.user_id, request.session_id)
        assistant_intent = classify_assistant_intent(request.message)
        intent_result = parse_intent(request.message)
        extracted_parameters = extract_parameters(request.message)
        existing_state = self._state_store.get(request.user_id, session_id)

        if (
            assistant_intent != "unknown"
            and executable_intent_for(assistant_intent) is None
        ):
            policy_decision = decide_response_policy(
                user_message=request.message,
                assistant_intent=assistant_intent,
                financial_context_summary=None,
            )
            answer_plan = build_answer_plan(
                user_message=request.message,
                assistant_intent=assistant_intent,
                response_policy_decision=policy_decision,
            )
            if existing_state is not None:
                self._state_store.clear(request.user_id, session_id)
            return build_policy_response(
                intent_result,
                extracted_parameters,
                assistant_intent=assistant_intent,
                policy_decision=policy_decision,
                answer_plan=answer_plan,
                session_id=session_id,
                active_intent_before=(
                    existing_state.active_intent if existing_state is not None else None
                ),
                state_cleared=existing_state is not None,
            )

        resolved_turn = self._dialogue_manager.resolve_turn(
            user_id=request.user_id,
            session_id=session_id,
            parsed_intent=intent_result,
            extracted_parameters=extracted_parameters,
            existing_state=existing_state,
        )

        if resolved_turn.state_cleared:
            self._state_store.clear(request.user_id, session_id)

        if resolved_turn.intent == "unknown":
            return build_unknown_response(
                intent_result,
                resolved_turn.parameters,
                session_id=session_id,
                active_intent_before=resolved_turn.active_intent_before,
                active_intent_after=resolved_turn.active_intent_after,
                state_continued=resolved_turn.state_continued,
                state_cleared=resolved_turn.state_cleared,
            )

        missing_fields = _missing_fields(resolved_turn.intent, resolved_turn.parameters)
        if missing_fields:
            resolved_assistant_intent = _assistant_intent_for_resolved_intent(
                resolved_turn.intent
            )
            policy_decision = decide_response_policy(
                user_message=request.message,
                assistant_intent=resolved_assistant_intent,
                financial_context_summary=_demo_financial_context_summary(),
                missing_fields=missing_fields,
            )
            self._save_pending_state(
                request=request,
                session_id=session_id,
                resolved_turn=resolved_turn,
                missing_fields=missing_fields,
                existing_state=existing_state,
            )
            return build_missing_info_response(
                intent_result.model_copy(update={"intent": resolved_turn.intent}),
                resolved_turn.parameters,
                missing_fields,
                session_id=session_id,
                assistant_intent=resolved_assistant_intent,
                policy_decision=policy_decision,
                active_intent_before=resolved_turn.active_intent_before,
                active_intent_after=resolved_turn.intent,
                state_continued=resolved_turn.state_continued,
                state_cleared=False,
            )

        execution = execute_tool(
            resolved_turn.intent,
            request.user_id,
            resolved_turn.parameters,
            self._tools,
            self._decision_engine,
        )
        resolved_assistant_intent = _assistant_intent_for_resolved_intent(
            resolved_turn.intent
        )
        policy_decision = decide_response_policy(
            user_message=request.message,
            assistant_intent=resolved_assistant_intent,
            financial_context_summary=_demo_financial_context_summary(),
            calculation_result=execution.result,
        )
        self._state_store.clear(request.user_id, session_id)
        return build_answered_response(
            intent_result.model_copy(update={"intent": resolved_turn.intent}),
            resolved_turn.parameters,
            execution,
            session_id=session_id,
            assistant_intent=resolved_assistant_intent,
            policy_decision=policy_decision,
            active_intent_before=resolved_turn.active_intent_before,
            active_intent_after=None,
            state_continued=resolved_turn.state_continued,
            state_cleared=True,
        )

    def _save_pending_state(
        self,
        *,
        request: ChatMessageRequest,
        session_id: str,
        resolved_turn: ResolvedDialogueTurn,
        missing_fields: list[str],
        existing_state: ConversationState | None,
    ) -> None:
        now = datetime.now(UTC)
        turn_count = (
            existing_state.turn_count + 1
            if resolved_turn.state_continued and existing_state is not None
            else 1
        )
        created_at = (
            existing_state.created_at
            if resolved_turn.state_continued and existing_state is not None
            else now
        )
        self._state_store.save(
            ConversationState(
                user_id=request.user_id,
                session_id=session_id,
                active_intent=resolved_turn.intent,
                collected_parameters=resolved_turn.parameters,
                missing_fields=missing_fields,
                last_status="needs_more_info",
                created_at=created_at,
                updated_at=now,
                turn_count=turn_count,
            )
        )


def _resolve_session_id(user_id: str, session_id: str | None) -> str:
    if session_id is not None and session_id.strip():
        return session_id.strip()
    return f"default:{user_id}"


def _missing_fields(intent: IntentName, parameters: ExtractedParameters) -> list[str]:
    if intent == "simulate_purchase" and parameters.amount_minor is None:
        return ["amount"]

    if intent == "simulate_installments":
        missing_fields: list[str] = []
        if parameters.amount_minor is None:
            missing_fields.append("amount")
        if parameters.months is None:
            missing_fields.append("months")
        return missing_fields

    return []


def _assistant_intent_for_resolved_intent(intent: IntentName) -> AssistantIntent:
    if intent == "cashflow_status":
        return AssistantIntent.CASHFLOW_STATUS
    if intent == "weekly_spend":
        return AssistantIntent.WEEKLY_SAFE_SPEND
    if intent == "overdraft_risk":
        return AssistantIntent.OVERDRAFT_RISK
    if intent == "upcoming_expenses":
        return AssistantIntent.UPCOMING_EXPENSES
    if intent == "simulate_purchase":
        return AssistantIntent.AFFORDABILITY_CHECK
    if intent == "simulate_installments":
        return AssistantIntent.PAYMENT_SPLIT_SIMULATION
    return AssistantIntent.UNKNOWN


def _demo_financial_context_summary() -> dict[str, bool]:
    return {
        "has_transactions": True,
        "has_current_balance": True,
        "has_salary_date": True,
        "has_recurring_expenses": True,
        "has_upcoming_expenses": True,
        "has_live_bank_data": False,
    }
