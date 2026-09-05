from typing import Protocol
from uuid import UUID

from app.domain.entities.sync_log import SyncLog


class SyncLogRepository(Protocol):
    async def create(self, sync_log: SyncLog) -> SyncLog: ...

    async def list_by_item_id(
        self,
        pluggy_item_id: UUID,
        limit: int = 50,
    ) -> list[SyncLog]: ...
