from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.financial.contracts import Currency, RiskLevel

IntentName = Literal[
    "cashflow_status",
    "simulate_purchase",
    "simulate_installments",
    "unknown",
]
ResponseStatus = Literal["answered", "needs_more_info", "unknown", "error"]


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


class IntentParseResult(BaseModel):
    intent: IntentName
    confidence: float = Field(ge=0.0, le=1.0)
    matched_rule: str | None
    normalized_message: str


class ExtractedParameters(BaseModel):
    amount_minor: int | None = None
    currency: Currency | None = None
    months: int | None = None


class ChatDebugInfo(BaseModel):
    normalized_message: str
    matched_rule: str | None
    parameters: ExtractedParameters
    tool_executed: bool
    risk_level: RiskLevel | None = None


class ChatMessageResponse(BaseModel):
    answer: str
    intent: IntentName
    status: ResponseStatus
    tool_called: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: list[str]
    debug: ChatDebugInfo
