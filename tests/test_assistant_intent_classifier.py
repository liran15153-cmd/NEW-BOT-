from app.ai.assistant_intent_classifier import (
    classify_assistant_intent,
    executable_intent_for,
)
from app.ai.assistant_policy_schemas import AssistantIntent


def test_assistant_intents_map_only_supported_flows_to_executable_intents() -> None:
    assert executable_intent_for(AssistantIntent.CASHFLOW_STATUS) == "cashflow_status"
    assert executable_intent_for(AssistantIntent.AFFORDABILITY_CHECK) == "simulate_purchase"
    assert (
        executable_intent_for(AssistantIntent.PAYMENT_SPLIT_SIMULATION)
        == "simulate_installments"
    )


def test_future_or_safety_assistant_intents_do_not_map_to_financial_tools() -> None:
    assert executable_intent_for(AssistantIntent.RECURRING_EXPENSES) is None
    assert executable_intent_for(AssistantIntent.MONEY_LEAK_DETECTION) is None
    assert executable_intent_for(AssistantIntent.TRANSACTION_EXPLANATION) is None
    assert executable_intent_for(AssistantIntent.PRIVACY_QUESTION) is None
    assert executable_intent_for(AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE) is None
    assert executable_intent_for(AssistantIntent.UNSUPPORTED_LOAN_ADVICE) is None
    assert executable_intent_for(AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE) is None
    assert executable_intent_for(AssistantIntent.GENERAL_HELP) is None
    assert executable_intent_for(AssistantIntent.UNKNOWN) is None


def test_classifier_detects_hebrew_supported_financial_intents() -> None:
    assert (
        classify_assistant_intent("כמה יישאר לי עד המשכורת?")
        == AssistantIntent.CASHFLOW_STATUS
    )
    assert (
        classify_assistant_intent("אפשר לקנות אוזניות ב-400 שקל?")
        == AssistantIntent.AFFORDABILITY_CHECK
    )
    assert (
        classify_assistant_intent("מה יקרה אם אפרוס 900 שקל ל-3 תשלומים?")
        == AssistantIntent.PAYMENT_SPLIT_SIMULATION
    )


def test_classifier_detects_hebrew_future_product_intents() -> None:
    assert (
        classify_assistant_intent("איזה מנויים יש לי?")
        == AssistantIntent.RECURRING_EXPENSES
    )
    assert (
        classify_assistant_intent("איפה נוזל לי כסף?")
        == AssistantIntent.MONEY_LEAK_DETECTION
    )
    assert (
        classify_assistant_intent("מה העסקה הזאת אומרת?")
        == AssistantIntent.TRANSACTION_EXPLANATION
    )


def test_future_product_messages_are_recognized_but_not_executable() -> None:
    future_messages = (
        "איזה מנויים יש לי?",
        "איפה נוזל לי כסף?",
        "מה העסקה הזאת אומרת?",
    )

    for message in future_messages:
        assistant_intent = classify_assistant_intent(message)
        assert executable_intent_for(assistant_intent) is None


def test_classifier_detects_privacy_and_unsupported_advice_before_amounts() -> None:
    assert (
        classify_assistant_intent("המעסיק רואה את השאלות שלי?")
        == AssistantIntent.PRIVACY_QUESTION
    )
    assert (
        classify_assistant_intent("כדאי להשקיע 400 שקל במניה?")
        == AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE
    )
    assert (
        classify_assistant_intent("האם לקחת הלוואה של 1000 שקל?")
        == AssistantIntent.UNSUPPORTED_LOAN_ADVICE
    )
    assert (
        classify_assistant_intent("יש פה עצת מס או משהו משפטי?")
        == AssistantIntent.UNSUPPORTED_TAX_OR_LEGAL_ADVICE
    )


def test_classifier_detects_english_intents_and_unknown_requests() -> None:
    assert (
        classify_assistant_intent("can I afford headphones for 400 shekels?")
        == AssistantIntent.AFFORDABILITY_CHECK
    )
    assert classify_assistant_intent("until payday") == AssistantIntent.CASHFLOW_STATUS
    assert (
        classify_assistant_intent("what subscriptions do I have?")
        == AssistantIntent.RECURRING_EXPENSES
    )
    assert (
        classify_assistant_intent("should I invest in this stock?")
        == AssistantIntent.UNSUPPORTED_INVESTMENT_ADVICE
    )
    assert (
        classify_assistant_intent("should I take a loan?")
        == AssistantIntent.UNSUPPORTED_LOAN_ADVICE
    )
    assert classify_assistant_intent("tell me a joke") == AssistantIntent.UNKNOWN
