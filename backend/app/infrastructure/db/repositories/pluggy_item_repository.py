from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.pluggy_item import PluggyItem
from app.infrastructure.db.models.pluggy_item import PluggyItemModel


class SqlAlchemyPluggyItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, model: PluggyItemModel) -> PluggyItem:
        return PluggyItem(
            id=model.id,
            user_id=model.user_id,
            pluggy_item_id=model.pluggy_item_id,
            connector_id=model.connector_id,
            connector_name=model.connector_name,
            status=model.status,
            last_synced_at=model.last_synced_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: PluggyItem) -> PluggyItemModel:
        return PluggyItemModel(
            id=entity.id,
            user_id=entity.user_id,
            pluggy_item_id=entity.pluggy_item_id,
            connector_id=entity.connector_id,
            connector_name=entity.connector_name,
            status=entity.status,
            last_synced_at=entity.last_synced_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, item_id: UUID) -> PluggyItem | None:
        query = select(PluggyItemModel).where(PluggyItemModel.id == item_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_pluggy_item_id(self, pluggy_item_id: str) -> PluggyItem | None:
        query = select(PluggyItemModel).where(
            PluggyItemModel.pluggy_item_id == pluggy_item_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_user_id(self, user_id: UUID) -> list[PluggyItem]:
        query = (
            select(PluggyItemModel)
            .where(PluggyItemModel.user_id == user_id)
            .order_by(PluggyItemModel.created_at.desc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, item: PluggyItem) -> PluggyItem:
        model = self._to_model(item)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def update(self, item: PluggyItem) -> PluggyItem:
        query = select(PluggyItemModel).where(PluggyItemModel.id == item.id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            return await self.create(item)

        model.connector_id = item.connector_id
        model.connector_name = item.connector_name
        model.status = item.status
        model.last_synced_at = item.last_synced_at
        model.updated_at = item.updated_at
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, item_id: UUID) -> bool:
        query = select(PluggyItemModel).where(PluggyItemModel.id == item_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

