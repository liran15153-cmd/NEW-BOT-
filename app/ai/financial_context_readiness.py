from app.ai.assistant_policy_schemas import (
    AssistantIntent,
    DataReadinessLevel,
    DataReadinessResult,
    FinancialContextSummary,
)

_PROJECTION_INTENTS = {
    AssistantIntent.CASHFLOW_STATUS,
    AssistantIntent.WEEKLY_SAFE_SPEND,
    AssistantIntent.OVERDRAFT_RISK,
    AssistantIntent.UPCOMING_EXPENSES,
    AssistantIntent.AFFORDABILITY_CHECK,
    AssistantIntent.PAYMENT_SPLIT_SIMULATION,
}
_TRANSACTION_HISTORY_INTENTS = {
    AssistantIntent.RECURRING_EXPENSES,
    AssistantIntent.MONEY_LEAK_DETECTION,
    AssistantIntent.TRANSACTION_EXPLANATION,
}


def evaluate_financial_context_readiness(
    financial_context_summary: FinancialContextSummary | dict | None,
    *,
    assistant_intent: AssistantIntent | None = None,
) -> DataReadinessResult:
    summary = _normalize_summary(financial_context_summary)
    if summary is None or not _has_any_financial_data(summary):
        return DataReadinessResult(
            level=DataReadinessLevel.NONE,
            can_answer=False,
            missing_fields=["financial_data"],
            must_include_uncertainty=True,
            reason="no_financial_data",
        )

    has_balance = _has_current_balance(summary)
    has_salary = _has_salary_date(summary)
    has_transactions = summary.has_transactions is True
    warnings = _readiness_warnings(summary)
    missing_fields = _missing_fields(
        has_balance=has_balance,
        has_salary=has_salary,
        has_transactions=has_transactions,
        has_upcoming_expenses=summary.has_upcoming_expenses is True,
        assistant_intent=assistant_intent,
    )
    level = _readiness_level(
        has_balance=has_balance,
        has_salary=has_salary,
        has_transactions=has_transactions,
        has_recurring_expenses=summary.has_recurring_expenses is True,
        has_upcoming_expenses=summary.has_upcoming_expenses is True,
    )
    can_answer = _can_answer(
        level=level,
        missing_fields=missing_fields,
        assistant_intent=assistant_intent,
    )

    return DataReadinessResult(
        level=level,
        can_answer=can_answer,
        missing_fields=missing_fields,
        warnings=warnings,
        must_include_uncertainty=_must_include_uncertainty(
            level=level,
            warnings=warnings,
            assistant_intent=assistant_intent,
        ),
        reason=_reason(level, missing_fields),
    )


def _normalize_summary(
    financial_context_summary: FinancialContextSummary | dict | None,
) -> FinancialContextSummary | None:
    if financial_context_summary is None:
        return None
    if isinstance(financial_context_summary, FinancialContextSummary):
        return financial_context_summary
    return FinancialContextSummary.model_validate(financial_context_summary)


def _has_any_financial_data(summary: FinancialContextSummary) -> bool:
    return any(
        (
            summary.current_balance_minor is not None,
            summary.has_current_balance is True,
            summary.next_salary_date is not None,
            summary.has_salary_date is True,
            summary.has_transactions is True,
            summary.has_recurring_expenses is True,
            summary.has_upcoming_expenses is True,
            summary.has_imported_data is True,
            summary.has_live_bank_data is True,
        )
    )


def _has_current_balance(summary: FinancialContextSummary) -> bool:
    return summary.has_current_balance is True or summary.current_balance_minor is not None


def _has_salary_date(summary: FinancialContextSummary) -> bool:
    return summary.has_salary_date is True or summary.next_salary_date is not None


def _readiness_warnings(summary: FinancialContextSummary) -> list[str]:
    warnings = list(summary.import_warnings)
    if summary.possible_duplicates:
        warnings.append("possible_duplicates")
    return warnings


def _missing_fields(
    *,
    has_balance: bool,
    has_salary: bool,
    has_transactions: bool,
    has_upcoming_expenses: bool,
    assistant_intent: AssistantIntent | None,
) -> list[str]:
    missing_fields: list[str] = []
    if assistant_intent in _TRANSACTION_HISTORY_INTENTS and not has_transactions:
        missing_fields.append("transactions")
    if assistant_intent in _PROJECTION_INTENTS:
        if not has_balance:
            missing_fields.append("current_balance")
        if not has_salary:
            missing_fields.append("next_salary_date")
    if (
        assistant_intent == AssistantIntent.UPCOMING_EXPENSES
        and not has_upcoming_expenses
    ):
        missing_fields.append("upcoming_expenses")
    return missing_fields


def _readiness_level(
    *,
    has_balance: bool,
    has_salary: bool,
    has_transactions: bool,
    has_recurring_expenses: bool,
    has_upcoming_expenses: bool,
) -> DataReadinessLevel:
    if has_balance and has_salary and has_transactions and (
        has_recurring_expenses or has_upcoming_expenses
    ):
        return DataReadinessLevel.HIGH
    if has_transactions and has_salary:
        return DataReadinessLevel.MEDIUM
    if has_transactions or has_balance or has_salary:
        return DataReadinessLevel.LOW
    return DataReadinessLevel.NONE


def _can_answer(
    *,
    level: DataReadinessLevel,
    missing_fields: list[str],
    assistant_intent: AssistantIntent | None,
) -> bool:
    if level == DataReadinessLevel.NONE:
        return False
    if assistant_intent in _PROJECTION_INTENTS and missing_fields:
        if assistant_intent == AssistantIntent.UPCOMING_EXPENSES:
            return False
        return level == DataReadinessLevel.MEDIUM and missing_fields == [
            "current_balance"
        ]
    if assistant_intent in _TRANSACTION_HISTORY_INTENTS and "transactions" in missing_fields:
        return False
    return level in {DataReadinessLevel.MEDIUM, DataReadinessLevel.HIGH}


def _must_include_uncertainty(
    *,
    level: DataReadinessLevel,
    warnings: list[str],
    assistant_intent: AssistantIntent | None,
) -> bool:
    return bool(
        warnings
        or level in {DataReadinessLevel.NONE, DataReadinessLevel.MEDIUM}
        or assistant_intent in _PROJECTION_INTENTS
    )


def _reason(level: DataReadinessLevel, missing_fields: list[str]) -> str | None:
    if level == DataReadinessLevel.NONE:
        return "no_financial_data"
    if missing_fields:
        return "missing_required_financial_context"
    return None
