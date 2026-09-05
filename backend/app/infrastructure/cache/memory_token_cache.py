import asyncio
from datetime import UTC, datetime, timedelta

from app.infrastructure.cache.token_cache import PluggyTokenCache


class MemoryTokenCache(PluggyTokenCache):
    """Cache de token da Pluggy em memória do processo com suporte a renovação proativa (ADR-004).

    Por padrão, o apiKey da Pluggy tem validade de 2 horas (7200s).
    A renovação proativa considera o token expirado quando faltam menos de
    `proactive_margin_seconds` (padrão: 600s = 10 minutos) para sua expiração real,
    evitando que requisições falhem por expiração iminente.
    """

    def __init__(self, proactive_margin_seconds: int = 600) -> None:
        self._token: str | None = None
        self._expires_at: datetime | None = None
        self._proactive_margin_seconds = proactive_margin_seconds
        self._lock = asyncio.Lock()

    async def get_token(self) -> str | None:
        async with self._lock:
            if not self._token or not self._expires_at:
                return None

            now = datetime.now(UTC)
            # Renovação proativa: se a validade restante for inferior à margem de segurança,
            # considera como expirado para que uma nova chave seja obtida preventivamente.
            if (
                now + timedelta(seconds=self._proactive_margin_seconds)
                >= self._expires_at
            ):
                return None

            return self._token

    async def set_token(self, token: str, expires_in_seconds: int = 7200) -> None:
        async with self._lock:
            self._token = token
            self._expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)

    async def invalidate(self) -> None:
        async with self._lock:
            self._token = None
            self._expires_at = None

    @property
    def expires_at(self) -> datetime | None:
        return self._expires_at
