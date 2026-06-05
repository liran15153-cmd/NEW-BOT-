from fastapi import APIRouter

from app.ai.router import ChatRouter
from app.ai.schemas import ChatMessageRequest, ChatMessageResponse
from app.financial.mock_tools import DemoFinancialTools

router = APIRouter(prefix="/chat", tags=["chat"])

chat_router_service = ChatRouter(tools=DemoFinancialTools())


@router.post("/message", response_model=ChatMessageResponse)
def post_chat_message(request: ChatMessageRequest) -> ChatMessageResponse:
    return chat_router_service.route(request)
