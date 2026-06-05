from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

IntentName = Literal[
    "cashflow_status",
    "simulate_purchase",
    "simulate_installments",
    "unknown",
]


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)

    @field_validator("user_id", "message")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank.")
        return cleaned


class ChatMessageResponse(BaseModel):
    answer: str
    intent: IntentName
    tool_called: str
    confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: list[str]
