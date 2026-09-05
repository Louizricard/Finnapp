from app.application.dto.pluggy_dto import (
    PluggyItemOutputDto,
    RegisterItemInputDto,
)
from app.core.logging import get_logger
from app.domain.entities.pluggy_item import PluggyItem
from app.domain.entities.sync_log import SyncLog
from app.domain.repositories.pluggy_item_repository import PluggyItemRepository
from app.domain.repositories.sync_log_repository import SyncLogRepository
from app.infrastructure.pluggy.client import PluggyClient

logger = get_logger("register_pluggy_item")


class RegisterPluggyItemUseCase:
    """Caso de uso para registrar e persistir um novo Item criado via widget Pluggy Connect (RF-011/012)."""

    def __init__(
        self,
        item_repo: PluggyItemRepository,
        pluggy_client: PluggyClient,
        sync_log_repo: SyncLogRepository,
    ) -> None:
        self.item_repo = item_repo
        self.pluggy_client = pluggy_client
        self.sync_log_repo = sync_log_repo

    async def execute(self, dto: RegisterItemInputDto) -> PluggyItemOutputDto:
        existing = await self.item_repo.get_by_pluggy_item_id(dto.item_id)

        connector_id = dto.connector_id
        connector_name = dto.connector_name
        status = "UPDATING"

        # Tenta enriquecer dados com a API da Pluggy
        try:
            item_data = await self.pluggy_client.get_item(dto.item_id)
            status = item_data.status or "UPDATING"
            if item_data.connector:
                connector_id = item_data.connector.id
                connector_name = item_data.connector.name
        except Exception as e:
            logger.warning(
                "pluggy_fetch_item_failed_using_defaults",
                item_id=dto.item_id,
                error=str(e),
            )

        if existing:
            existing.status = status
            if connector_id is not None:
                existing.connector_id = connector_id
            if connector_name is not None:
                existing.connector_name = connector_name
            saved_item = await self.item_repo.update(existing)
        else:
            new_item = PluggyItem(
                user_id=dto.user_id,
                pluggy_item_id=dto.item_id,
                connector_id=connector_id,
                connector_name=connector_name,
                status=status,
            )
            saved_item = await self.item_repo.create(new_item)

        # Registra auditoria inicial em sync_logs
        await self.sync_log_repo.create(
            SyncLog(
                pluggy_item_id=saved_item.id,
                event_type="item/registered",
                status="SUCCESS",
                payload={
                    "item_id": dto.item_id,
                    "connector_id": connector_id,
                    "connector_name": connector_name,
                    "status": status,
                },
            )
        )

        return PluggyItemOutputDto(
            id=saved_item.id,
            user_id=saved_item.user_id,
            pluggy_item_id=saved_item.pluggy_item_id,
            connector_id=saved_item.connector_id,
            connector_name=saved_item.connector_name,
            status=saved_item.status,
            last_synced_at=saved_item.last_synced_at,
            created_at=saved_item.created_at,
            updated_at=saved_item.updated_at,
        )
