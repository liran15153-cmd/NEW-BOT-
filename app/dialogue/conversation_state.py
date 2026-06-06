from datetime import datetime

from pydantic import BaseModel, Field

from app.ai.chat_message_schemas import ExtractedParameters, IntentName, ResponseStatus


class LastToolResult(BaseModel):
    tool_called: str | None = None
    risk_level: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


class ConversationState(BaseModel):
    user_id: str
    session_id: str
    active_intent: IntentName
    collected_parameters: ExtractedParameters
    missing_fields: list[str]
    last_tool_result: LastToolResult | None = None
    last_status: ResponseStatus | None = None
    created_at: datetime
    updated_at: datetime
    turn_count: int = 1

    @classmethod
    def new(
        cls,
        *,
        user_id: str,
        session_id: str,
        active_intent: IntentName,
        collected_parameters: ExtractedParameters,
        missing_fields: list[str],
        now: datetime,
    ) -> "ConversationState":
        return cls(
            user_id=user_id,
            session_id=session_id,
            active_intent=active_intent,
            collected_parameters=collected_parameters,
            missing_fields=missing_fields,
            last_status="needs_more_info",
            created_at=now,
            updated_at=now,
            turn_count=1,
        )


