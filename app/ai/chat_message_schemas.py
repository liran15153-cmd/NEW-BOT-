from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ai.assistant_policy_schemas import (
    AssistantIntent,
    DataReadinessLevel,
    ResponseType,
)
from app.financial.financial_contracts import Currency, RiskLevel
from app.financial.financial_reason_codes import ReasonCode

IntentName = Literal[
    "cashflow_status",
    "simulate_purchase",
    "simulate_installments",
    "affordability_check",
    "payment_split_simulation",
    "recurring_expenses",
    "money_leak_detection",
    "transaction_explanation",
    "privacy_question",
    "unsupported_investment_advice",
    "unsupported_loan_advice",
    "unsupported_tax_or_legal_advice",
    "safety_boundary_request",
    "general_help",
    "unknown",
]
ResponseStatus = Literal["answered", "needs_more_info", "unknown", "error"]


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    session_id: str | None = None

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
    session_id: str
    normalized_message: str
    matched_rule: str | None
    parameters: ExtractedParameters
    assistant_intent: AssistantIntent | None = None
    response_type: ResponseType | None = None
    policy_allowed: bool | None = None
    policy_reason: str | None = None
    blocked_reason: str | None = None
    data_readiness_level: DataReadinessLevel | None = None
    required_disclaimers: list[str] = Field(default_factory=list)
    active_intent_before: IntentName | None = None
    active_intent_after: IntentName | None = None
    state_continued: bool = False
    state_cleared: bool = False
    tool_executed: bool
    risk_level: RiskLevel | None = None
    reason_codes: list[ReasonCode] = Field(default_factory=list)


class ChatMessageResponse(BaseModel):
    answer: str
    intent: IntentName
    status: ResponseStatus
    tool_called: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: list[str]
    debug: ChatDebugInfo


