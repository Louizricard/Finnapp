from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.db.models.user import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserModel).where(
            func.lower(UserModel.email) == email.lower().strip()
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def count(self) -> int:
        query = select(func.count()).select_from(UserModel)
        result = await self.session.execute(query)
        return int(result.scalar_one() or 0)
