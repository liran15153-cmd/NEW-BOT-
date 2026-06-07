from typing import Any

import anyio
import httpx

from app.main import create_app


HE_CASHFLOW_QUESTION = (
    "\u05db\u05de\u05d4 \u05e0\u05e9\u05d0\u05e8 \u05dc\u05d9 "
    "\u05e2\u05d3 \u05d4\u05de\u05e9\u05db\u05d5\u05e8\u05ea?"
)
HE_FINANCIAL_DATA = (
    "\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd "
    "\u05e4\u05d9\u05e0\u05e0\u05e1\u05d9\u05d9\u05dd"
)
HE_DEMO = "\u05d3\u05de\u05d5"

PROFILE_PAYLOAD = {
    "user_id": "profile_user",
    "as_of_date": "2026-06-07",
    "current_balance_minor": 250000,
    "next_salary_date": "2026-06-16",
    "safety_buffer_minor": 20000,
    "committed_obligations": [
        {
            "label": "rent",
            "amount_minor": 120000,
            "due_date": "2026-06-10",
            "currency": "ILS",
        },
        {
            "label": "utilities",
            "amount_minor": 30000,
            "due_date": "2026-06-12",
            "currency": "ILS",
        },
        {
            "label": "after salary",
            "amount_minor": 40000,
            "due_date": "2026-06-20",
            "currency": "ILS",
        },
    ],
}


def test_chat_without_financial_profile_asks_for_real_user_data() -> None:
    body = anyio.run(
        _post_chat_with_app,
        create_app(),
        {
            "user_id": "missing_profile_user",
            "message": HE_CASHFLOW_QUESTION,
        },
    )

    assert body["intent"] == "cashflow_status"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["missing_fields"] == ["financial_data"]
    assert body["debug"]["tool_executed"] is False
    assert body["debug"]["response_type"] == "ask_for_missing_data"
    assert body["debug"]["data_readiness_level"] == "none"
    assert HE_FINANCIAL_DATA in body["answer"]
    assert HE_DEMO not in body["answer"]


def test_financial_profile_post_enables_grounded_cashflow_answer() -> None:
    app = create_app()

    profile_response, chat_body = anyio.run(
        _post_profile_then_chat,
        app,
        PROFILE_PAYLOAD,
        {
            "user_id": "profile_user",
            "message": HE_CASHFLOW_QUESTION,
        },
    )

    assert profile_response.status_code == 200
    profile_body = profile_response.json()
    assert profile_body["status"] == "stored"
    assert profile_body["readiness"]["can_answer"] is True
    assert profile_body["readiness"]["level"] == "high"

    assert chat_body["intent"] == "cashflow_status"
    assert chat_body["status"] == "answered"
    assert chat_body["tool_called"] == "cashflow_status"
    assert chat_body["debug"]["tool_executed"] is True
    assert chat_body["debug"]["risk_level"] == "medium"
    assert "1000" in chat_body["answer"]
    assert "800" in chat_body["answer"]
    assert HE_DEMO not in chat_body["answer"]


def test_financial_profile_rejects_past_obligations() -> None:
    payload = {
        **PROFILE_PAYLOAD,
        "user_id": "bad_profile_user",
        "committed_obligations": [
            {
                "label": "past charge",
                "amount_minor": 12000,
                "due_date": "2026-06-01",
                "currency": "ILS",
            }
        ],
    }

    response = anyio.run(_post_profile, create_app(), payload)

    assert response.status_code == 422


async def _post_profile(app, payload: dict[str, Any]) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.post("/financial/profile", json=payload)


async def _post_chat_with_app(app, payload: dict[str, Any]) -> dict[str, Any]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/chat/message", json=payload)
    assert response.status_code == 200
    return response.json()


async def _post_profile_then_chat(
    app,
    profile_payload: dict[str, Any],
    chat_payload: dict[str, Any],
) -> tuple[httpx.Response, dict[str, Any]]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        profile_response = await client.post("/financial/profile", json=profile_payload)
        chat_response = await client.post("/chat/message", json=chat_payload)

    assert chat_response.status_code == 200
    return profile_response, chat_response.json()
