from app.application.dto.auth_dto import (
    RegisterRequestDto,
    TokenResponseDto,
    UserResponseDto,
)
from app.core.config import settings
from app.core.exceptions import ConflictException, ForbiddenException
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
)
from app.domain.entities.user import RefreshToken, User
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.user_repo = user_repository
        self.refresh_repo = refresh_token_repository

    async def execute(self, dto: RegisterRequestDto) -> TokenResponseDto:
        # Protect single user creation with SETUP_TOKEN
        if dto.setup_token != settings.SETUP_TOKEN:
            raise ForbiddenException("Setup token inválido")

        # Single user policy check
        total_users = await self.user_repo.count()
        if total_users > 0:
            raise ConflictException("Sistema já possui um usuário cadastrado")

        existing_user = await self.user_repo.get_by_email(dto.email)
        if existing_user:
            raise ConflictException("Email já cadastrado no sistema")

        hashed_pw = hash_password(dto.password)
        new_user = User(
            email=dto.email.lower().strip(),
            password_hash=hashed_pw,
            full_name=dto.full_name,
        )
        created_user = await self.user_repo.create(new_user)

        # Issue tokens
        access_token = create_access_token(
            created_user.id,
            created_user.email,
        )
        raw_refresh, token_hash, expires_at = generate_refresh_token()
        refresh_entity = RefreshToken(
            user_id=created_user.id,
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
                id=created_user.id,
                email=created_user.email,
                full_name=created_user.full_name,
                created_at=created_user.created_at,
                updated_at=created_user.updated_at,
            ),
        )
