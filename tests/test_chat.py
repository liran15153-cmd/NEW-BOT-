from tests.support import post_json


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
    assert body == {
        "answer": (
            "Based on the demo financial context, this purchase is possible "
            "but would leave a low buffer until salary day."
        ),
        "intent": "simulate_purchase",
        "tool_called": "simulate_purchase",
        "confidence": 0.85,
        "missing_fields": [],
    }


def test_cashflow_question_maps_to_cashflow_status() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "How is my cashflow this month?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "cashflow_status"
    assert body["tool_called"] == "cashflow_status"
    assert body["confidence"] == 0.9
    assert body["missing_fields"] == []


def test_purchase_without_amount_returns_missing_amount() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Can I buy headphones?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_purchase"
    assert body["tool_called"] == "none"
    assert body["confidence"] == 0.75
    assert body["missing_fields"] == ["amount"]
    assert "amount" in body["answer"].lower()


def test_installment_question_maps_to_simulate_installments() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Can I split 1200 shekels over 6 months?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["tool_called"] == "simulate_installments"
    assert body["confidence"] == 0.8
    assert body["missing_fields"] == []
    assert "6 months" in body["answer"]


def test_installment_question_missing_amount_and_months_returns_missing_fields() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Can I split this into payments?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "simulate_installments"
    assert body["tool_called"] == "none"
    assert body["confidence"] == 0.7
    assert body["missing_fields"] == ["amount", "installment_count"]


def test_unknown_message_returns_unknown_intent() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "Tell me a joke",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": (
            "I could not match this message to a supported demo financial "
            "intent yet."
        ),
        "intent": "unknown",
        "tool_called": "none",
        "confidence": 0.2,
        "missing_fields": [],
    }


def test_chat_message_requires_non_empty_user_id_and_message() -> None:
    response = post_json(
        "/chat/message",
        {"user_id": " ", "message": ""},
    )

    assert response.status_code == 422
