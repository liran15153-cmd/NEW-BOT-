from typing import Any

import anyio
import httpx

from app.main import create_app
from app.financial.user_financial_profile import (
    FinancialObligation,
    FinancialProfileSnapshot,
)


def synthetic_financial_profile(user_id: str) -> FinancialProfileSnapshot:
    return FinancialProfileSnapshot(
        user_id=user_id,
        as_of_date="2026-06-07",
        current_balance_minor=250000,
        next_salary_date="2026-06-16",
        safety_buffer_minor=20000,
        committed_obligations=[
            FinancialObligation(
                label="near term utility",
                amount_minor=10000,
                due_date="2026-06-09",
            ),
            FinancialObligation(
                label="near term insurance",
                amount_minor=10000,
                due_date="2026-06-11",
            ),
            FinancialObligation(
                label="near term rent",
                amount_minor=45000,
                due_date="2026-06-12",
            ),
            FinancialObligation(
                label="card payment before salary",
                amount_minor=115000,
                due_date="2026-06-15",
            ),
        ],
    )


def seed_financial_profile(app, user_id: str) -> None:
    app.state.financial_profile_store.save(synthetic_financial_profile(user_id))


def get(path: str) -> httpx.Response:
    return anyio.run(_request, "GET", path, None)


def post_json(path: str, payload: dict[str, Any]) -> httpx.Response:
    return anyio.run(_request, "POST", path, payload)


async def _request(
    method: str,
    path: str,
    payload: dict[str, Any] | None,
) -> httpx.Response:
    app = create_app()
    if payload is not None and "user_id" in payload:
        seed_financial_profile(app, str(payload["user_id"]))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, json=payload)


