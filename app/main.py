from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.chat_message_api import router as chat_router
from app.api.health_check_api import router as health_router
from app.api.local_tester_api import router as tester_router
from app.core.app_settings import settings
from app.dialogue.conversation_state_store import (
    ConversationStateStore,
    InMemoryConversationStateStore,
)
from app.financial.financial_contracts import FinancialTools
from app.financial.financial_decision_engine import FinancialDecisionEngine
from app.financial.demo_financial_tools import DemoFinancialTools

_APP_DIR = Path(__file__).resolve().parent
_TESTER_ASSETS_DIR = _APP_DIR / "tester" / "assets"


def create_app(
    *,
    tools: FinancialTools | None = None,
    state_store: ConversationStateStore | None = None,
    decision_engine: FinancialDecisionEngine | None = None,
) -> FastAPI:
    app = FastAPI(title=settings.service_name)
    app.state.financial_tools = tools or DemoFinancialTools()
    app.state.conversation_state_store = (
        state_store or InMemoryConversationStateStore()
    )
    app.state.financial_decision_engine = decision_engine or FinancialDecisionEngine()
    app.mount(
        "/tester/assets",
        StaticFiles(directory=_TESTER_ASSETS_DIR),
        name="tester-assets",
    )
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(tester_router)
    return app


app = create_app()


