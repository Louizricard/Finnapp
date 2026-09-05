from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import RefreshToken
from app.infrastructure.db.models.refresh_token import RefreshTokenModel


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            created_at=model.created_at,
        )

    def _to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            revoked_at=entity.revoked_at,
            created_at=entity.created_at,
        )

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        model = self._to_model(refresh_token)
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def revoke(self, token_id: UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)
        await self.session.flush()
