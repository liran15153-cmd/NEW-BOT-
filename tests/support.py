from typing import Any

import anyio
import httpx

from app.main import create_app


def get(path: str) -> httpx.Response:
    return anyio.run(_request, "GET", path, None)


def post_json(path: str, payload: dict[str, Any]) -> httpx.Response:
    return anyio.run(_request, "POST", path, payload)


async def _request(
    method: str,
    path: str,
    payload: dict[str, Any] | None,
) -> httpx.Response:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, json=payload)
