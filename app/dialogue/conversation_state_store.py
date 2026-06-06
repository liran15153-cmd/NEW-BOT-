from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.dialogue.conversation_state import ConversationState


class ConversationStateStore(Protocol):
    def get(self, user_id: str, session_id: str) -> ConversationState | None:
        ...

    def save(self, state: ConversationState) -> None:
        ...

    def clear(self, user_id: str, session_id: str) -> None:
        ...

    def clear_all(self) -> None:
        ...


class InMemoryConversationStateStore:
    def __init__(
        self,
        *,
        now_fn: Callable[[], datetime] | None = None,
        ttl: timedelta = timedelta(minutes=15),
    ) -> None:
        self._states: dict[tuple[str, str], ConversationState] = {}
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._ttl = ttl

    def get(self, user_id: str, session_id: str) -> ConversationState | None:
        key = (user_id, session_id)
        state = self._states.get(key)
        if state is None:
            return None
        if self._is_expired(state):
            self._states.pop(key, None)
            return None
        return state

    def save(self, state: ConversationState) -> None:
        self._states[(state.user_id, state.session_id)] = state

    def clear(self, user_id: str, session_id: str) -> None:
        self._states.pop((user_id, session_id), None)

    def clear_all(self) -> None:
        self._states.clear()

    def _is_expired(self, state: ConversationState) -> bool:
        return self._now_fn() - state.updated_at > self._ttl


