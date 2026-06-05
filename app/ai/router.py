from app.ai.intent_parser import parse_intent
from app.ai.parameter_extractor import extract_parameters
from app.ai.response_builder import (
    build_answered_response,
    build_missing_info_response,
    build_unknown_response,
)
from app.ai.schemas import ChatMessageRequest, ChatMessageResponse, ExtractedParameters, IntentName
from app.ai.tool_executor import execute_tool
from app.financial.contracts import FinancialTools


class ChatRouter:
    def __init__(self, tools: FinancialTools) -> None:
        self._tools = tools

    def route(self, request: ChatMessageRequest) -> ChatMessageResponse:
        intent_result = parse_intent(request.message)
        parameters = extract_parameters(request.message)

        if intent_result.intent == "unknown":
            return build_unknown_response(intent_result, parameters)

        missing_fields = _missing_fields(intent_result.intent, parameters)
        if missing_fields:
            return build_missing_info_response(
                intent_result,
                parameters,
                missing_fields,
            )

        execution = execute_tool(
            intent_result.intent,
            request.user_id,
            parameters,
            self._tools,
        )
        return build_answered_response(intent_result, parameters, execution)


def _missing_fields(intent: IntentName, parameters: ExtractedParameters) -> list[str]:
    if intent == "simulate_purchase" and parameters.amount_minor is None:
        return ["amount"]

    if intent == "simulate_installments":
        missing_fields: list[str] = []
        if parameters.amount_minor is None:
            missing_fields.append("amount")
        if parameters.months is None:
            missing_fields.append("months")
        return missing_fields

    return []
