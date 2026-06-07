from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.ai.assistant_policy_schemas import AssistantIntent, DataReadinessResult
from app.ai.financial_context_readiness import evaluate_financial_context_readiness
from app.financial.user_financial_profile import (
    FinancialProfileSnapshot,
    financial_context_summary,
)

router = APIRouter(prefix="/financial", tags=["financial"])


class FinancialProfileWriteResponse(BaseModel):
    status: str
    user_id: str
    readiness: DataReadinessResult


@router.post("/profile", response_model=FinancialProfileWriteResponse)
def post_financial_profile(
    profile: FinancialProfileSnapshot,
    request: Request,
) -> FinancialProfileWriteResponse:
    request.app.state.financial_profile_store.save(profile)
    readiness = evaluate_financial_context_readiness(
        financial_context_summary(profile),
        assistant_intent=AssistantIntent.CASHFLOW_STATUS,
    )
    return FinancialProfileWriteResponse(
        status="stored",
        user_id=profile.user_id,
        readiness=readiness,
    )
