from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResponseType(str, Enum):
    DIRECT_ANSWER = "direct_answer"
    CAUTIOUS_ESTIMATE = "cautious_estimate"
    ASK_FOR_MISSING_DATA = "ask_for_missing_data"
    CLARIFYING_QUESTION = "clarifying_question"
    UNSUPPORTED_REQUEST = "unsupported_request"
    PRIVACY_EXPLANATION = "privacy_explanation"
    ERROR_FALLBACK = "error_fallback"


class AssistantIntent(str, Enum):
    CASHFLOW_STATUS = "cashflow_status"
    WEEKLY_SAFE_SPEND = "weekly_safe_spend"
    AFFORDABILITY_CHECK = "affordability_check"
    PAYMENT_SPLIT_SIMULATION = "payment_split_simulation"
    RECURRING_EXPENSES = "recurring_expenses"
    MONEY_LEAK_DETECTION = "money_leak_detection"
    TRANSACTION_EXPLANATION = "transaction_explanation"
    PRIVACY_QUESTION = "privacy_question"
    UNSUPPORTED_INVESTMENT_ADVICE = "unsupported_investment_advice"
    UNSUPPORTED_LOAN_ADVICE = "unsupported_loan_advice"
    UNSUPPORTED_TAX_OR_LEGAL_ADVICE = "unsupported_tax_or_legal_advice"
    SAFETY_BOUNDARY_REQUEST = "safety_boundary_request"
    GENERAL_HELP = "general_help"
    UNKNOWN = "unknown"


class DataReadinessLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FinancialContextSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    current_balance_minor: int | None = None
    has_current_balance: bool | None = None
    next_salary_date: str | None = None
    has_salary_date: bool | None = None
    has_transactions: bool | None = None
    latest_transaction_date: str | None = None
    has_recurring_expenses: bool | None = None
    has_upcoming_expenses: bool | None = None
    has_imported_data: bool | None = None
    has_live_bank_data: bool | None = None
    possible_duplicates: bool = False
    import_warnings: list[str] = Field(default_factory=list)


class DataReadinessResult(BaseModel):
    level: DataReadinessLevel
    can_answer: bool
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    must_include_uncertainty: bool = False
    reason: str | None = None


class ResponsePolicyDecision(BaseModel):
    allowed: bool
    response_type: ResponseType
    blocked_reason: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    required_disclaimers: list[str] = Field(default_factory=list)
    must_include_uncertainty: bool = False
    risk_level: str | None = None
    reason: str | None = None
    data_readiness: DataReadinessResult | None = None


class AnswerPlan(BaseModel):
    response_type: ResponseType
    main_message_key: str
    numbers_to_include: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    required_disclaimer_keys: list[str] = Field(default_factory=list)
    tone: str = "practical_non_judgmental"
