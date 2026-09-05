from app.application.dto.auth_dto import (
    RefreshTokenRequestDto,
    TokenResponseDto,
    UserResponseDto,
)
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.domain.entities.user import RefreshToken
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.user_repository import UserRepository


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.user_repo = user_repository
        self.refresh_repo = refresh_token_repository

    async def execute(self, dto: RefreshTokenRequestDto) -> TokenResponseDto:
        token_hash = hash_refresh_token(dto.refresh_token)
        stored_token = await self.refresh_repo.get_by_token_hash(token_hash)

        if not stored_token or not stored_token.is_active:
            # If token was already revoked, potential reuse attack: revoke all for user
            if stored_token and stored_token.revoked_at is not None:
                await self.refresh_repo.revoke_all_for_user(stored_token.user_id)
            raise UnauthorizedException("Refresh token inválido ou expirado")

        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user:
            raise UnauthorizedException("Usuário não encontrado")

        # Refresh Token Rotation: revoke previous token immediately
        await self.refresh_repo.revoke(stored_token.id)

        # Issue new token pair
        access_token = create_access_token(user.id, user.email)
        raw_refresh, new_hash, expires_at = generate_refresh_token()

        new_refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=expires_at,
        )
        await self.refresh_repo.create(new_refresh_entity)

        return TokenResponseDto(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponseDto(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )
