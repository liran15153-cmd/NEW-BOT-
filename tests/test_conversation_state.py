from datetime import UTC, datetime, timedelta

from app.ai.chat_message_schemas import ExtractedParameters
from app.dialogue.conversation_flow_manager import DialogueManager
from app.dialogue.conversation_state import ConversationState
from app.dialogue.conversation_state_store import InMemoryConversationStateStore
from app.financial.financial_contracts import Currency


def test_state_store_supports_save_get_clear_and_clear_all() -> None:
    now = datetime(2026, 6, 6, 10, 0, tzinfo=UTC)
    store = InMemoryConversationStateStore(now_fn=lambda: now)
    state = ConversationState.new(
        user_id="user_123",
        session_id="session_123",
        active_intent="simulate_purchase",
        collected_parameters=ExtractedParameters(),
        missing_fields=["amount"],
        now=now,
    )

    store.save(state)
    assert store.get("user_123", "session_123") == state

    store.clear("user_123", "session_123")
    assert store.get("user_123", "session_123") is None

    store.save(state)
    store.clear_all()
    assert store.get("user_123", "session_123") is None


def test_state_expiry_is_testable_without_sleeping() -> None:
    now = datetime(2026, 6, 6, 10, 0, tzinfo=UTC)
    store = InMemoryConversationStateStore(
        now_fn=lambda: now,
        ttl=timedelta(minutes=15),
    )
    old_state = ConversationState.new(
        user_id="user_123",
        session_id="session_123",
        active_intent="simulate_purchase",
        collected_parameters=ExtractedParameters(),
        missing_fields=["amount"],
        now=now - timedelta(minutes=16),
    )

    store.save(old_state)

    assert store.get("user_123", "session_123") is None


def test_dialogue_manager_continues_pending_purchase_with_parameter_only_message() -> None:
    now = datetime(2026, 6, 6, 10, 0, tzinfo=UTC)
    state = ConversationState.new(
        user_id="user_123",
        session_id="session_123",
        active_intent="simulate_purchase",
        collected_parameters=ExtractedParameters(),
        missing_fields=["amount"],
        now=now,
    )

    resolved = DialogueManager(now_fn=lambda: now).resolve_turn(
        user_id="user_123",
        session_id="session_123",
        parsed_intent=_intent("unknown", 0.2),
        extracted_parameters=ExtractedParameters(
            amount_minor=40000,
            currency=Currency.ILS,
        ),
        existing_state=state,
    )

    assert resolved.intent == "simulate_purchase"
    assert resolved.parameters.amount_minor == 40000
    assert resolved.state_continued is True
    assert resolved.active_intent_before == "simulate_purchase"


def test_dialogue_manager_overrides_pending_state_with_clear_new_topic() -> None:
    now = datetime(2026, 6, 6, 10, 0, tzinfo=UTC)
    state = ConversationState.new(
        user_id="user_123",
        session_id="session_123",
        active_intent="simulate_purchase",
        collected_parameters=ExtractedParameters(),
        missing_fields=["amount"],
        now=now,
    )

    resolved = DialogueManager(now_fn=lambda: now).resolve_turn(
        user_id="user_123",
        session_id="session_123",
        parsed_intent=_intent("cashflow_status", 0.9),
        extracted_parameters=ExtractedParameters(),
        existing_state=state,
    )

    assert resolved.intent == "cashflow_status"
    assert resolved.state_continued is False
    assert resolved.state_cleared is True
    assert resolved.active_intent_before == "simulate_purchase"


def test_dialogue_manager_expires_over_turn_pending_state() -> None:
    now = datetime(2026, 6, 6, 10, 0, tzinfo=UTC)
    state = ConversationState.new(
        user_id="user_123",
        session_id="session_123",
        active_intent="simulate_purchase",
        collected_parameters=ExtractedParameters(),
        missing_fields=["amount"],
        now=now,
    ).model_copy(update={"turn_count": 6})

    resolved = DialogueManager(now_fn=lambda: now, max_pending_turns=6).resolve_turn(
        user_id="user_123",
        session_id="session_123",
        parsed_intent=_intent("unknown", 0.2),
        extracted_parameters=ExtractedParameters(
            amount_minor=40000,
            currency=Currency.ILS,
        ),
        existing_state=state,
    )

    assert resolved.intent == "unknown"
    assert resolved.state_continued is False
    assert resolved.state_cleared is True


def _intent(intent: str, confidence: float):
    from app.ai.chat_message_schemas import IntentParseResult

    return IntentParseResult(
        intent=intent,
        confidence=confidence,
        matched_rule=None if intent == "unknown" else f"{intent}_rule",
        normalized_message="normalized",
    )


