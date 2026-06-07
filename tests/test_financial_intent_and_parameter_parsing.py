from pathlib import Path

import pytest

from app.ai.financial_intent_parser import parse_intent
from app.ai.financial_parameter_extractor import extract_amount_minor, extract_months


@pytest.mark.parametrize(
    ("message", "expected_minor"),
    [
        ("אפשר לקנות את זה ב-400 שקל?", 40000),
        ("אפשר לקנות את זה ב-400 ש\"ח?", 40000),
        ("אפשר לקנות את זה ב-400 שח?", 40000),
        ("אפשר לקנות את זה ב-400 ₪?", 40000),
        ("אפשר לקנות את זה ב-₪400?", 40000),
        ("אפשר לקנות את זה ב-1,200 שקל?", 120000),
        ("אפשר לקנות את זה ב-1200 שקל?", 120000),
        ("Can I buy this for 400 nis?", 40000),
        ("Can I buy this for 400 shekels?", 40000),
    ],
)
def test_extract_amount_minor_supports_hebrew_and_ils_formats(
    message: str,
    expected_minor: int,
) -> None:
    assert extract_amount_minor(message) == expected_minor


def test_extract_amount_minor_ignores_installment_count_when_no_amount_exists() -> None:
    assert extract_amount_minor("Can I split this over 6 months?") is None


@pytest.mark.parametrize(
    ("message", "expected_months"),
    [
        ("מה יקרה אם אפרוס 900 שקל ל-3 תשלומים?", 3),
        ("מה יקרה אם אפרוס 900 שקל ל־3 תשלומים?", 3),
        ("מה יקרה אם אפרוס 900 שקל ב-3 תשלומים?", 3),
        ("מה יקרה אם אפרוס 900 שקל ב־3 תשלומים?", 3),
        ("מה יקרה אם אפרוס 900 שקל 3 תשלומים?", 3),
        ("Split 1200 shekels over 3 months", 3),
        ("Split 1200 shekels for 3 months", 3),
    ],
)
def test_extract_months_supports_hebrew_and_english_payment_phrases(
    message: str,
    expected_months: int,
) -> None:
    assert extract_months(message) == expected_months


def test_parse_intent_supports_hebrew_financial_messages() -> None:
    assert parse_intent("מה מצב התזרים שלי?").intent == "cashflow_status"
    assert parse_intent("כמה אפשר להוציא השבוע?").intent == "weekly_spend"
    assert parse_intent("האם אני אכנס למינוס לפני המשכורת?").intent == "overdraft_risk"
    assert parse_intent("אפשר לקנות את זה?").intent == "simulate_purchase"
    assert parse_intent("מה יקרה אם אפרוס לתשלומים?").intent == "simulate_installments"
    assert parse_intent("Tell me a joke").intent == "unknown"


def test_parse_intent_detects_weekly_safe_spend_before_generic_spend() -> None:
    hebrew = parse_intent("מה הסכום הבטוח שאפשר להוציא השבוע?")
    english = parse_intent("How much can I safely spend this week?")

    assert hebrew.intent == "weekly_spend"
    assert hebrew.matched_rule == "weekly_spend_keyword"
    assert english.intent == "weekly_spend"
    assert english.matched_rule == "weekly_spend_keyword"


def test_parse_intent_detects_overdraft_risk_before_generic_cashflow() -> None:
    hebrew = parse_intent("האם אני עלול להיכנס למינוס לפני המשכורת?")
    english = parse_intent("Am I likely to enter overdraft before payday?")

    assert hebrew.intent == "overdraft_risk"
    assert hebrew.matched_rule == "overdraft_risk_keyword"
    assert english.intent == "overdraft_risk"
    assert english.matched_rule == "overdraft_risk_keyword"


def test_router_contains_no_regex_patterns_or_user_facing_text() -> None:
    source = Path("app/ai/chat_router.py").read_text(encoding="utf-8")

    assert "re.compile" not in source
    assert "Based on" not in source
    assert "I need" not in source
    assert not any("\u0590" <= character <= "\u05ff" for character in source)

