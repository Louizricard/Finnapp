from uuid import UUID

from app.application.dto.pluggy_dto import ConnectTokenOutputDto
from app.infrastructure.pluggy.client import PluggyClient


class CreateConnectTokenUseCase:
    """Caso de uso para geração de connectToken para o widget Pluggy Connect (RF-010)."""

    def __init__(self, pluggy_client: PluggyClient) -> None:
        self.pluggy_client = pluggy_client

    async def execute(self, user_id: UUID) -> ConnectTokenOutputDto:
        token_response = await self.pluggy_client.create_connect_token(
            client_user_id=str(user_id)
        )
        return ConnectTokenOutputDto(
            access_token=token_response.access_token,
            connect_token=token_response.access_token,
        )
