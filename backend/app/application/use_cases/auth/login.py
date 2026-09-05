from app.application.dto.auth_dto import (
    LoginRequestDto,
    TokenResponseDto,
    UserResponseDto,
)
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    verify_password,
)
from app.domain.entities.user import RefreshToken
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.user_repository import UserRepository


class LoginUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.user_repo = user_repository
        self.refresh_repo = refresh_token_repository

    async def execute(self, dto: LoginRequestDto) -> TokenResponseDto:
        user = await self.user_repo.get_by_email(dto.email)
        if not user or not verify_password(dto.password, user.password_hash):
            raise UnauthorizedException("Email ou senha incorretos")

        access_token = create_access_token(user.id, user.email)
        raw_refresh, token_hash, expires_at = generate_refresh_token()

        refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.refresh_repo.create(refresh_entity)

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
