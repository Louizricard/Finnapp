from app.core.security import hash_refresh_token
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)


class LogoutUseCase:
    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.refresh_repo = refresh_token_repository

    async def execute(self, raw_refresh_token: str) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        stored_token = await self.refresh_repo.get_by_token_hash(token_hash)
        if stored_token and stored_token.revoked_at is None:
            await self.refresh_repo.revoke(stored_token.id)
