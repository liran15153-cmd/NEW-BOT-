from tests.api_test_client import post_json


def _assert_hebrew_answer(answer: str) -> None:
    assert any("\u0590" <= character <= "\u05ff" for character in answer)


def test_loan_request_with_purchase_words_does_not_execute_purchase_tool() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "האם לקחת הלוואה כדי לקנות משהו ב-1000 שקל?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_called"] is None
    assert body["debug"]["tool_executed"] is False
    assert body["debug"]["assistant_intent"] == "unsupported_loan_advice"
    assert body["debug"]["response_type"] == "unsupported_request"
    assert body["debug"]["policy_allowed"] is False
    assert body["debug"]["blocked_reason"] == "loan_recommendation_not_supported"
    assert body["status"] == "answered"
    assert body["intent"] == "unsupported_loan_advice"
    assert "הלוואה" in body["answer"]
    _assert_hebrew_answer(body["answer"])


def test_privacy_request_with_purchase_words_does_not_execute_purchase_tool() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "המעסיק רואה אם אפשר לקנות משהו ב-400 שקל?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_called"] is None
    assert body["debug"]["tool_executed"] is False
    assert body["debug"]["assistant_intent"] == "privacy_question"
    assert body["debug"]["response_type"] == "privacy_explanation"
    assert body["debug"]["policy_allowed"] is True
    assert body["debug"]["blocked_reason"] is None
    assert body["status"] == "answered"
    assert body["intent"] == "privacy_question"
    assert "מעסיק" in body["answer"]
    _assert_hebrew_answer(body["answer"])


def test_future_recurring_expenses_request_requires_transaction_history() -> None:
    response = post_json(
        "/chat/message",
        {
            "user_id": "user_123",
            "message": "איזה מנויים יש לי?",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "recurring_expenses"
    assert body["status"] == "needs_more_info"
    assert body["tool_called"] is None
    assert body["missing_fields"] == ["transactions"]
    assert body["debug"]["tool_executed"] is False
    assert body["debug"]["assistant_intent"] == "recurring_expenses"
    assert "עסקאות" in body["answer"]
    _assert_hebrew_answer(body["answer"])
