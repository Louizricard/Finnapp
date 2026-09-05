import pytest

from app.infrastructure.cache.memory_token_cache import MemoryTokenCache


@pytest.mark.asyncio
async def test_get_token_when_empty() -> None:
    cache = MemoryTokenCache()
    assert await cache.get_token() is None


@pytest.mark.asyncio
async def test_set_and_get_valid_token() -> None:
    cache = MemoryTokenCache()
    await cache.set_token("test-api-key", expires_in_seconds=7200)

    token = await cache.get_token()
    assert token == "test-api-key"
    assert cache.expires_at is not None


@pytest.mark.asyncio
async def test_invalidate_token() -> None:
    cache = MemoryTokenCache()
    await cache.set_token("test-api-key", expires_in_seconds=7200)
    assert await cache.get_token() == "test-api-key"

    await cache.invalidate()
    assert await cache.get_token() is None
    assert cache.expires_at is None


@pytest.mark.asyncio
async def test_proactive_renewal_margin() -> None:
    # Margem proativa de 600 segundos (10 minutos)
    cache = MemoryTokenCache(proactive_margin_seconds=600)

    # Token com 500 segundos restantes está dentro da janela de renovação proativa -> deve retornar None
    await cache.set_token("imminent-expiry-key", expires_in_seconds=500)
    assert await cache.get_token() is None

    # Token com 700 segundos restantes ainda tem mais de 10 minutos de margem -> deve retornar o token
    await cache.set_token("safe-key", expires_in_seconds=700)
    assert await cache.get_token() == "safe-key"
