from typing import Any

import httpx

from app.core.exceptions import BadGatewayException
from app.core.logging import get_logger
from app.infrastructure.cache.memory_token_cache import MemoryTokenCache
from app.infrastructure.cache.token_cache import PluggyTokenCache
from app.infrastructure.pluggy.schemas import (
    PluggyAuthResponse,
    PluggyConnectTokenResponse,
    PluggyItemResponse,
)

logger = get_logger("pluggy_client")


class PluggyClient:
    """Cliente HTTP assíncrono para a API da Pluggy."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.pluggy.ai",
        token_cache: PluggyTokenCache | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.token_cache = token_cache or MemoryTokenCache()
        self._http_client = http_client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is not None:
            return self._http_client
        return httpx.AsyncClient(timeout=15.0)

    async def authenticate(self, force_refresh: bool = False) -> str:
        """Autentica na Pluggy via POST /auth e armazena o apiKey no cache."""
        if not force_refresh:
            cached_token = await self.token_cache.get_token()
            if cached_token:
                return cached_token

        if not self.client_id or not self.client_secret:
            raise BadGatewayException(
                "Credenciais da Pluggy não configuradas (PLUGGY_CLIENT_ID / PLUGGY_CLIENT_SECRET ausentes)"
            )

        url = f"{self.base_url}/auth"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }

        client = await self._get_client()
        try:
            response = await client.post(url, json=payload)
        finally:
            if self._http_client is None:
                await client.aclose()

        if response.status_code != 200:
            logger.error(
                "pluggy_auth_failed",
                status_code=response.status_code,
                response=response.text,
            )
            raise BadGatewayException(
                f"Falha na autenticação com a Pluggy: {response.status_code} - {response.text}"
            )

        auth_data = PluggyAuthResponse.model_validate(response.json())
        await self.token_cache.set_token(auth_data.api_key, expires_in_seconds=7200)
        return auth_data.api_key

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Executa requisição autenticada com reautenticação automática em caso de 401."""
        api_key = await self.authenticate()
        url = f"{self.base_url}{path}"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

        client = await self._get_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
            )

            # Se o token expirou remotamente (401), invalida cache e tenta uma segunda vez
            if response.status_code == 401:
                logger.info("pluggy_token_expired_retrying")
                await self.token_cache.invalidate()
                new_key = await self.authenticate(force_refresh=True)
                headers["X-API-KEY"] = new_key
                response = await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )
        finally:
            if self._http_client is None:
                await client.aclose()

        if response.status_code >= 400:
            logger.error(
                "pluggy_request_failed",
                method=method,
                path=path,
                status_code=response.status_code,
                response=response.text,
            )
            raise BadGatewayException(
                f"Erro na comunicação com a Pluggy ({response.status_code}): {response.text}"
            )

        return response

    async def create_connect_token(
        self,
        client_user_id: str | None = None,
        item_id: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> PluggyConnectTokenResponse:
        """Emite connectToken temporário para inicialização do widget Pluggy Connect (RF-010)."""
        payload: dict[str, Any] = {}
        if item_id:
            payload["itemId"] = item_id

        opts = dict(options or {})
        if client_user_id:
            opts["clientUserId"] = client_user_id

        if opts:
            payload["options"] = opts

        response = await self._request("POST", "/connect_token", json=payload)
        return PluggyConnectTokenResponse.model_validate(response.json())

    async def get_item(self, item_id: str) -> PluggyItemResponse:
        """Consulta status e metadados de uma conexão (Item) na Pluggy."""
        response = await self._request("GET", f"/items/{item_id}")
        return PluggyItemResponse.model_validate(response.json())
