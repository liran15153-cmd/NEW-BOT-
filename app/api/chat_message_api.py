from fastapi import APIRouter, Request

from app.ai.chat_router import ChatRouter
from app.ai.chat_message_schemas import ChatMessageRequest, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
def post_chat_message(
    chat_request: ChatMessageRequest,
    request: Request,
) -> ChatMessageResponse:
    chat_router_service = ChatRouter(
        tools=request.app.state.financial_tools,
        state_store=request.app.state.conversation_state_store,
        decision_engine=request.app.state.financial_decision_engine,
    )
    return chat_router_service.route(chat_request)


