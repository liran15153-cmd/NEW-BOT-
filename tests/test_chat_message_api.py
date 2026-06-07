from tests.api_test_client import post_json


def _assert_hebrew_answer(answer: str) -> None:
    assert any("\u0590" <= character <= "\u05ff" for character in answer)


def test_chat_message_returns_structured_purchase_response() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Can I buy headphones for 400 shekels?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["status"] == "answered"
    assert body["tool_called"] == "simulate_purchase"
    assert body["confidence"] == 0.85
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is True
    assert body["debug"]["parameters"]["amount_minor"] == 40000
    assert body["debug"]["parameters"]["currency"] == "ILS"
    assert body["debug"]["risk_level"] == "medium"
    _assert_hebrew_answer(body["answer"])


def test_hebrew_cashflow_question_maps_to_cashflow_status() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "מה מצב התזרים שלי החודש?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "cashflow_status"
    assert body["status"] == "answered"
    assert body["tool_called"] == "cashflow_status"
    assert body["confidence"] == 0.9
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(body["answer"])


def test_weekly_safe_spend_question_returns_deterministic_projection() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "כמה אפשר להוציא השבוע?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "weekly_spend"
    assert body["status"] == "answered"
    assert body["tool_called"] == "weekly_spend"
    assert body["confidence"] == 0.88
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is True
    assert body["debug"]["assistant_intent"] == "weekly_safe_spend"
    assert body["debug"]["risk_level"] == "medium"
    assert "388.88" in body["answer"]
    assert "השבוע" in body["answer"]
    _assert_hebrew_answer(body["answer"])


def test_overdraft_risk_question_returns_deterministic_projection() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "האם אני אכנס למינוס לפני המשכורת?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "overdraft_risk"
    assert body["status"] == "answered"
    assert body["tool_called"] == "overdraft_risk"
    assert body["confidence"] == 0.87
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is True
    assert body["debug"]["assistant_intent"] == "overdraft_risk"
    assert body["debug"]["risk_level"] == "medium"
    assert "700" in body["answer"]
    assert "מינוס" in body["answer"]
    _assert_hebrew_answer(body["answer"])


def test_upcoming_expenses_question_returns_deterministic_pressure() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "איזה תשלומים קרובים יש לי?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "upcoming_expenses"
    assert body["status"] == "answered"
    assert body["tool_called"] == "upcoming_expenses"
    assert body["confidence"] == 0.86
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is True
    assert body["debug"]["assistant_intent"] == "upcoming_expenses"
    assert body["debug"]["risk_level"] == "medium"
    assert "650" in body["answer"]
    assert "קרובות" in body["answer"]
    _assert_hebrew_answer(body["answer"])


def test_hebrew_purchase_question_with_shekel_symbol_maps_to_simulate_purchase() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "אפשר לקנות אוזניות ב-₪400?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["status"] == "answered"
    assert body["tool_called"] == "simulate_purchase"
    assert body["missing_fields"] == []
    assert body["debug"]["parameters"]["amount_minor"] == 40000
    assert body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(body["answer"])


def test_hebrew_purchase_question_with_shekel_word_maps_to_simulate_purchase() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "האם אפשר לקנות את זה ב-400 שקל?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["status"] == "answered"
    assert body["tool_called"] == "simulate_purchase"
    assert body["missing_fields"] == []
    assert body["debug"]["parameters"]["amount_minor"] == 40000
    assert body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(body["answer"])


def test_purchase_without_amount_needs_more_info_and_does_not_call_tool() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "אפשר לקנות את זה?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["confidence"] == 0.75
    assert body["missing_fields"] == ["amount"]
    assert body["debug"]["tool_executed"] is False
    assert body["debug"]["parameters"]["amount_minor"] is None
    _assert_hebrew_answer(body["answer"])


def test_hebrew_installment_question_extracts_amount_and_months() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "מה יקרה אם אפרוס 900 שקל ל־3 תשלומים?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["status"] == "answered"
    assert body["tool_called"] == "simulate_installments"
    assert body["confidence"] == 0.8
    assert body["missing_fields"] == []
    assert body["debug"]["parameters"]["amount_minor"] == 90000
    assert body["debug"]["parameters"]["months"] == 3
    assert body["debug"]["tool_executed"] is True
    _assert_hebrew_answer(body["answer"])


def test_installments_without_amount_and_months_needs_more_info_and_does_not_call_tool() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "מה יקרה אם אפרוס לתשלומים?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["confidence"] == 0.7
    assert body["missing_fields"] == ["amount", "months"]
    assert body["debug"]["tool_executed"] is False
    _assert_hebrew_answer(body["answer"])


def test_installments_with_amount_but_without_months_needs_months_only() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "מה יקרה אם אפרוס 900 שקל?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["missing_fields"] == ["months"]
    assert body["debug"]["tool_executed"] is False


def test_installments_with_months_but_without_amount_needs_amount_only() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "מה יקרה אם אפרוס ל-3 תשלומים?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["missing_fields"] == ["amount"]
    assert body["debug"]["tool_executed"] is False


def test_unknown_message_returns_unknown_intent() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Tell me a joke",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "unknown"
    assert body["status"] == "unknown"
    assert body["tool_called"] is None
    assert body["confidence"] == 0.2
    assert body["missing_fields"] == []
    assert body["debug"]["tool_executed"] is False
    _assert_hebrew_answer(body["answer"])


def test_chat_message_requires_non_empty_user_id_and_message() -> None:
    response = post_json(
        "/chat/message",
        {"user_id": " ", "message": ""},
    )

    assert response.status_code == 422
