import anyio
import httpx

from app.main import create_app
from tests.api_test_client import seed_financial_profile


def _assert_hebrew_answer(answer: str) -> None:
    assert any("\u0590" <= character <= "\u05ff" for character in answer)


def post_message(
    message: str,
    *,
    user_id: str = "user_123",
    session_id: str | None = "session_123",
) -> httpx.Response:
    return anyio.run(_post_message, message, user_id, session_id)


async def _post_message(
    message: str,
    user_id: str,
    session_id: str | None,
) -> httpx.Response:
    app = create_app()
    seed_financial_profile(app, user_id)
    payload: dict[str, str] = {"user_id": user_id, "message": message}
    if session_id is not None:
        payload["session_id"] = session_id

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.post("/chat/message", json=payload)


def test_single_turn_purchase_still_works() -> None:
    response = post_message("אפשר לקנות משהו ב־400 שקל?")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["status"] == "answered"
    assert body["tool_called"] == "simulate_purchase"
    assert body["debug"]["session_id"] == "session_123"
    assert body["debug"]["state_continued"] is False
    assert body["debug"]["state_cleared"] is True
    assert body["debug"]["tool_executed"] is True
    assert body["debug"]["reason_codes"]
    _assert_hebrew_answer(body["answer"])


def test_multi_turn_purchase_continues_pending_intent() -> None:
    app = create_app()
    seed_financial_profile(app, "user_123")

    first = anyio.run(_post_with_app, app, "אפשר לקנות את זה?", "purchase_session")
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["intent"] == "simulate_purchase"
    assert first_body["status"] == "needs_more_info"
    assert first_body["tool_called"] is None
    assert first_body["missing_fields"] == ["amount"]
    assert first_body["debug"]["tool_executed"] is False
    assert first_body["debug"]["active_intent_after"] == "simulate_purchase"
    assert first_body["debug"]["state_cleared"] is False
    _assert_hebrew_answer(first_body["answer"])

    second = anyio.run(_post_with_app, app, "400 שקל", "purchase_session")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["intent"] == "simulate_purchase"
    assert second_body["status"] == "answered"
    assert second_body["tool_called"] == "simulate_purchase"
    assert second_body["missing_fields"] == []
    assert second_body["debug"]["parameters"]["amount_minor"] == 40000
    assert second_body["debug"]["state_continued"] is True
    assert second_body["debug"]["state_cleared"] is True
    assert second_body["debug"]["tool_executed"] is True
    assert second_body["debug"]["reason_codes"]
    _assert_hebrew_answer(second_body["answer"])


def test_multi_turn_installments_continues_pending_intent() -> None:
    app = create_app()
    seed_financial_profile(app, "user_123")

    first = anyio.run(_post_with_app, app, "מה יקרה אם אפרוס לתשלומים?", "installments_session")
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["intent"] == "simulate_installments"
    assert first_body["status"] == "needs_more_info"
    assert first_body["tool_called"] is None
    assert first_body["missing_fields"] == ["amount", "months"]

    second = anyio.run(_post_with_app, app, "900 שקל ל־3 תשלומים", "installments_session")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["intent"] == "simulate_installments"
    assert second_body["status"] == "answered"
    assert second_body["tool_called"] == "simulate_installments"
    assert second_body["debug"]["parameters"]["amount_minor"] == 90000
    assert second_body["debug"]["parameters"]["months"] == 3
    assert second_body["debug"]["state_continued"] is True
    assert second_body["debug"]["state_cleared"] is True
    assert second_body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(second_body["answer"])


def test_new_topic_overrides_pending_purchase() -> None:
    app = create_app()
    seed_financial_profile(app, "user_123")

    first = anyio.run(_post_with_app, app, "אפשר לקנות את זה?", "override_session")
    assert first.json()["status"] == "needs_more_info"

    second = anyio.run(_post_with_app, app, "כמה נשאר לי עד המשכורת?", "override_session")
    assert second.status_code == 200
    body = second.json()
    assert body["intent"] == "cashflow_status"
    assert body["status"] == "answered"
    assert body["tool_called"] == "cashflow_status"
    assert body["debug"]["active_intent_before"] == "simulate_purchase"
    assert body["debug"]["state_continued"] is False
    assert body["debug"]["state_cleared"] is True
    assert body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(body["answer"])


def test_missing_session_id_uses_default_user_session_key() -> None:
    app = create_app()
    seed_financial_profile(app, "user_with_default_session")

    first = anyio.run(
        _post_with_app,
        app,
        "אפשר לקנות את זה?",
        None,
        "user_with_default_session",
    )
    assert first.json()["debug"]["session_id"] == "default:user_with_default_session"
    assert first.json()["status"] == "needs_more_info"

    second = anyio.run(
        _post_with_app,
        app,
        "400 שקל",
        None,
        "user_with_default_session",
    )
    assert second.json()["status"] == "answered"
    assert second.json()["debug"]["state_continued"] is True


async def _post_with_app(
    app,
    message: str,
    session_id: str | None,
    user_id: str = "user_123",
) -> httpx.Response:
    payload: dict[str, str] = {"user_id": user_id, "message": message}
    if session_id is not None:
        payload["session_id"] = session_id

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.post("/chat/message", json=payload)


