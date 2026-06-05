from app.ai.router import extract_amount_minor, extract_installment_count


def test_extract_amount_minor_supports_ils_words_and_symbols() -> None:
    assert extract_amount_minor("Can I buy this for 400 shekels?") == 40000
    assert extract_amount_minor("Can I buy this for ₪99.90?") == 9990
    assert extract_amount_minor("Can I buy this for 150 NIS?") == 15000


def test_extract_amount_minor_ignores_installment_count_when_no_amount_exists() -> None:
    assert extract_amount_minor("Can I split this over 6 months?") is None


def test_extract_installment_count_supports_common_payment_phrases() -> None:
    assert extract_installment_count("Split 1200 shekels over 6 months") == 6
    assert extract_installment_count("Can I use 3 installments?") == 3
    assert extract_installment_count("Pay in 12 payments") == 12
