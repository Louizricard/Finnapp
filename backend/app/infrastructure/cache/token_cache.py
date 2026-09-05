from abc import ABC, abstractmethod


class PluggyTokenCache(ABC):
    """Interface abstrata para armazenamento em cache do token de autenticação (apiKey) da Pluggy."""

    @abstractmethod
    async def get_token(self) -> str | None:
        """Retorna o apiKey válido do cache se ainda não tiver expirado."""
        pass

    @abstractmethod
    async def set_token(self, token: str, expires_in_seconds: int = 7200) -> None:
        """Armazena o apiKey no cache com o tempo de expiração especificado."""
        pass

    @abstractmethod
    async def invalidate(self) -> None:
        """Invalida o token em cache forçando uma nova autenticação."""
        pass
