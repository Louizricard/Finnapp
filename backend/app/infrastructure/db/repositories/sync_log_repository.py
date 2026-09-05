from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.sync_log import SyncLog
from app.infrastructure.db.models.sync_log import SyncLogModel


class SqlAlchemySyncLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, model: SyncLogModel) -> SyncLog:
        return SyncLog(
            id=model.id,
            pluggy_item_id=model.pluggy_item_id,
            event_type=model.event_type,
            status=model.status,
            payload=model.payload,
            error_message=model.error_message,
            created_at=model.created_at,
        )

    def _to_model(self, entity: SyncLog) -> SyncLogModel:
        return SyncLogModel(
            id=entity.id,
            pluggy_item_id=entity.pluggy_item_id,
            event_type=entity.event_type,
            status=entity.status,
            payload=entity.payload,
            error_message=entity.error_message,
            created_at=entity.created_at,
        )

    async def create(self, sync_log: SyncLog) -> SyncLog:
        model = self._to_model(sync_log)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def list_by_item_id(
        self,
        pluggy_item_id: UUID,
        limit: int = 50,
    ) -> list[SyncLog]:
        query = (
            select(SyncLogModel)
            .where(SyncLogModel.pluggy_item_id == pluggy_item_id)
            .order_by(SyncLogModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
