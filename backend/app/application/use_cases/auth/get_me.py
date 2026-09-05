from uuid import UUID

from app.application.dto.auth_dto import UserResponseDto
from app.core.exceptions import EntityNotFoundException
from app.domain.repositories.user_repository import UserRepository


class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    async def execute(self, user_id: UUID) -> UserResponseDto:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("Usuário", user_id)

        return UserResponseDto(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
