from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel

from app.ai.chat_message_schemas import ExtractedParameters, IntentName, IntentParseResult
from app.dialogue.conversation_state import ConversationState


class ResolvedDialogueTurn(BaseModel):
    user_id: str
    session_id: str
    intent: IntentName
    parameters: ExtractedParameters
    active_intent_before: IntentName | None
    active_intent_after: IntentName | None
    state_continued: bool
    state_cleared: bool


class DialogueManager:
    def __init__(
        self,
        *,
        now_fn: Callable[[], datetime] | None = None,
        ttl: timedelta = timedelta(minutes=15),
        max_pending_turns: int = 6,
        new_topic_confidence: float = 0.8,
    ) -> None:
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._ttl = ttl
        self._max_pending_turns = max_pending_turns
        self._new_topic_confidence = new_topic_confidence

    def resolve_turn(
        self,
        *,
        user_id: str,
        session_id: str,
        parsed_intent: IntentParseResult,
        extracted_parameters: ExtractedParameters,
        existing_state: ConversationState | None,
    ) -> ResolvedDialogueTurn:
        if existing_state is None:
            return self._new_turn(
                user_id=user_id,
                session_id=session_id,
                parsed_intent=parsed_intent,
                parameters=extracted_parameters,
                state_cleared=False,
            )

        active_before = existing_state.active_intent
        if self._is_stale(existing_state):
            return self._new_turn(
                user_id=user_id,
                session_id=session_id,
                parsed_intent=parsed_intent,
                parameters=extracted_parameters,
                active_before=active_before,
                state_cleared=True,
            )

        if self._is_new_topic(parsed_intent, existing_state):
            return self._new_turn(
                user_id=user_id,
                session_id=session_id,
                parsed_intent=parsed_intent,
                parameters=extracted_parameters,
                active_before=active_before,
                state_cleared=True,
            )

        if self._should_continue(parsed_intent, extracted_parameters, existing_state):
            merged_parameters = _merge_parameters(
                existing_state.collected_parameters,
                extracted_parameters,
            )
            return ResolvedDialogueTurn(
                user_id=user_id,
                session_id=session_id,
                intent=existing_state.active_intent,
                parameters=merged_parameters,
                active_intent_before=active_before,
                active_intent_after=existing_state.active_intent,
                state_continued=True,
                state_cleared=False,
            )

        return self._new_turn(
            user_id=user_id,
            session_id=session_id,
            parsed_intent=parsed_intent,
            parameters=extracted_parameters,
            active_before=active_before,
            state_cleared=False,
        )

    def _new_turn(
        self,
        *,
        user_id: str,
        session_id: str,
        parsed_intent: IntentParseResult,
        parameters: ExtractedParameters,
        active_before: IntentName | None = None,
        state_cleared: bool,
    ) -> ResolvedDialogueTurn:
        active_after = None if parsed_intent.intent == "unknown" else parsed_intent.intent
        return ResolvedDialogueTurn(
            user_id=user_id,
            session_id=session_id,
            intent=parsed_intent.intent,
            parameters=parameters,
            active_intent_before=active_before,
            active_intent_after=active_after,
            state_continued=False,
            state_cleared=state_cleared,
        )

    def _is_stale(self, state: ConversationState) -> bool:
        if self._now_fn() - state.updated_at > self._ttl:
            return True
        return state.turn_count >= self._max_pending_turns

    def _is_new_topic(
        self,
        parsed_intent: IntentParseResult,
        state: ConversationState,
    ) -> bool:
        return (
            parsed_intent.intent != "unknown"
            and parsed_intent.intent != state.active_intent
            and parsed_intent.confidence >= self._new_topic_confidence
        )

    def _should_continue(
        self,
        parsed_intent: IntentParseResult,
        parameters: ExtractedParameters,
        state: ConversationState,
    ) -> bool:
        if parsed_intent.intent == state.active_intent:
            return True
        return parsed_intent.intent == "unknown" and _has_any_parameter(parameters)


def _has_any_parameter(parameters: ExtractedParameters) -> bool:
    return (
        parameters.amount_minor is not None
        or parameters.currency is not None
        or parameters.months is not None
    )


def _merge_parameters(
    existing: ExtractedParameters,
    new: ExtractedParameters,
) -> ExtractedParameters:
    return ExtractedParameters(
        amount_minor=new.amount_minor
        if new.amount_minor is not None
        else existing.amount_minor,
        currency=new.currency if new.currency is not None else existing.currency,
        months=new.months if new.months is not None else existing.months,
    )


