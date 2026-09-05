from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException, UnauthorizedException
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.repositories.refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.db.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(session)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> UUID:
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("Token inválido: sujeito não encontrado")
    try:
        return UUID(sub)
    except ValueError as err:
        raise UnauthorizedException("ID de usuário no token inválido") from err


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise EntityNotFoundException("Usuário", user_id)
    return user
