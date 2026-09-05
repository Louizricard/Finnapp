from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
import respx
from httpx import Response

from app.core.config import settings
from app.presentation.dependencies import _pluggy_token_cache


@pytest_asyncio.fixture(autouse=True)
async def reset_cache() -> AsyncGenerator[None, None]:
    if not settings.PLUGGY_CLIENT_ID:
        settings.PLUGGY_CLIENT_ID = "mock-client-id"
    if not settings.PLUGGY_CLIENT_SECRET:
        settings.PLUGGY_CLIENT_SECRET = "mock-client-secret"
    if not settings.PLUGGY_WEBHOOK_SECRET:
        settings.PLUGGY_WEBHOOK_SECRET = "test-webhook-secret"

    await _pluggy_token_cache.invalidate()
    yield
    await _pluggy_token_cache.invalidate()


async def _get_auth_token(client: httpx.AsyncClient) -> str:
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "pluggy_user@example.com",
            "password": "Password123!",
            "full_name": "Pluggy Test User",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    return str(res.json()["access_token"])


@pytest.mark.asyncio
@respx.mock
async def test_create_connect_token_unauthenticated(
    async_client: httpx.AsyncClient,
) -> None:
    res = await async_client.post("/api/v1/pluggy/connect-token")
    assert res.status_code == 401


@pytest.mark.asyncio
@respx.mock
async def test_create_connect_token_success_and_cache(
    async_client: httpx.AsyncClient,
) -> None:
    token = await _get_auth_token(async_client)
    headers = {"Authorization": f"Bearer {token}"}

    # Mock endpoints da Pluggy
    auth_route = respx.post(f"{settings.PLUGGY_BASE_URL}/auth").mock(
        return_value=Response(200, json={"apiKey": "fake-pluggy-api-key"})
    )
    connect_route = respx.post(f"{settings.PLUGGY_BASE_URL}/connect_token").mock(
        return_value=Response(200, json={"accessToken": "fake-connect-token-xyz-123"})
    )

    # 1. Primeira chamada: deve bater em /auth e /connect_token
    res = await async_client.post("/api/v1/pluggy/connect-token", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["connect_token"] == "fake-connect-token-xyz-123"
    assert data["access_token"] == "fake-connect-token-xyz-123"

    assert auth_route.call_count == 1
    assert connect_route.call_count == 1

    # 2. Segunda chamada: o apiKey deve vir do cache em memória, sem chamar /auth novamente
    res_cached = await async_client.post(
        "/api/v1/pluggy/connect-token", headers=headers
    )
    assert res_cached.status_code == 200
    assert res_cached.json()["connect_token"] == "fake-connect-token-xyz-123"

    assert auth_route.call_count == 1  # Não deve ter chamado /auth novamente!
    assert connect_route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_register_and_list_pluggy_items(
    async_client: httpx.AsyncClient,
) -> None:
    token = await _get_auth_token(async_client)
    headers = {"Authorization": f"Bearer {token}"}

    # Mock Pluggy auth & GET /items/item-123
    respx.post(f"{settings.PLUGGY_BASE_URL}/auth").mock(
        return_value=Response(200, json={"apiKey": "fake-pluggy-api-key"})
    )
    respx.get(f"{settings.PLUGGY_BASE_URL}/items/item-pluggy-abc").mock(
        return_value=Response(
            200,
            json={
                "id": "item-pluggy-abc",
                "status": "UPDATED",
                "executionStatus": "SUCCESS",
                "connector": {
                    "id": 201,
                    "name": "Banco Inter",
                },
            },
        )
    )

    # 1. Registrar item
    res_create = await async_client.post(
        "/api/v1/pluggy/items",
        headers=headers,
        json={"item_id": "item-pluggy-abc"},
    )
    assert res_create.status_code == 201
    item_data = res_create.json()
    assert item_data["pluggy_item_id"] == "item-pluggy-abc"
    assert item_data["connector_name"] == "Banco Inter"
    assert item_data["connector_id"] == 201
    assert item_data["status"] == "UPDATED"

    # 2. Listar itens
    res_list = await async_client.get("/api/v1/pluggy/items", headers=headers)
    assert res_list.status_code == 200
    items = res_list.json()
    assert len(items) == 1
    assert items[0]["pluggy_item_id"] == "item-pluggy-abc"


@pytest.mark.asyncio
async def test_webhook_security_and_logging(
    async_client: httpx.AsyncClient,
) -> None:
    # 1. Webhook com secret inválido no path -> 401
    res_invalid = await async_client.post(
        "/api/v1/webhooks/pluggy/wrong-secret",
        json={"event": "item/created", "itemId": "item-123"},
    )
    assert res_invalid.status_code == 401

    # 2. Webhook com secret correto no path -> 200 e salva em sync_logs
    valid_secret = settings.PLUGGY_WEBHOOK_SECRET
    payload = {
        "event": "item/created",
        "itemId": "item-webhook-123",
        "eventId": "evt-abc-999",
    }
    res_valid = await async_client.post(
        f"/api/v1/webhooks/pluggy/{valid_secret}",
        json=payload,
    )
    assert res_valid.status_code == 200
    assert res_valid.json() == {"received": True}

    # 3. Também deve funcionar na rota direta sem /api/v1
    res_direct = await async_client.post(
        f"/webhooks/pluggy/{valid_secret}",
        json=payload,
    )
    assert res_direct.status_code == 200
    assert res_direct.json() == {"received": True}
