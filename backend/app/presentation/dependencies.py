from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import EntityNotFoundException, UnauthorizedException
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.pluggy_item_repository import PluggyItemRepository
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.sync_log_repository import SyncLogRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.cache.memory_token_cache import MemoryTokenCache
from app.infrastructure.cache.token_cache import PluggyTokenCache
from app.infrastructure.db.repositories.pluggy_item_repository import (
    SqlAlchemyPluggyItemRepository,
)
from app.infrastructure.db.repositories.refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.db.repositories.sync_log_repository import (
    SqlAlchemySyncLogRepository,
)
from app.infrastructure.db.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.session import get_db_session
from app.infrastructure.pluggy.client import PluggyClient

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)

_pluggy_token_cache = MemoryTokenCache()


def get_pluggy_token_cache() -> PluggyTokenCache:
    return _pluggy_token_cache


def get_pluggy_client(
    token_cache: PluggyTokenCache = Depends(get_pluggy_token_cache),
) -> PluggyClient:
    return PluggyClient(
        client_id=settings.PLUGGY_CLIENT_ID,
        client_secret=settings.PLUGGY_CLIENT_SECRET,
        base_url=settings.PLUGGY_BASE_URL,
        token_cache=token_cache,
    )


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(session)


def get_pluggy_item_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PluggyItemRepository:
    return SqlAlchemyPluggyItemRepository(session)


def get_sync_log_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SyncLogRepository:
    return SqlAlchemySyncLogRepository(session)


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
