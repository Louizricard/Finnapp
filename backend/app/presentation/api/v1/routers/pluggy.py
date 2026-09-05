from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.dto.pluggy_dto import RegisterItemInputDto
from app.application.use_cases.pluggy.create_connect_token import (
    CreateConnectTokenUseCase,
)
from app.application.use_cases.pluggy.register_item import (
    RegisterPluggyItemUseCase,
)
from app.domain.repositories.pluggy_item_repository import PluggyItemRepository
from app.domain.repositories.sync_log_repository import SyncLogRepository
from app.infrastructure.pluggy.client import PluggyClient
from app.presentation.api.v1.schemas.pluggy import (
    ConnectTokenResponse,
    CreateItemRequest,
    PluggyItemResponse,
)
from app.presentation.dependencies import (
    get_current_user_id,
    get_pluggy_client,
    get_pluggy_item_repository,
    get_sync_log_repository,
)

router = APIRouter(prefix="/pluggy", tags=["Pluggy Open Finance"])


@router.post(
    "/connect-token",
    response_model=ConnectTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Gera connectToken para o widget Pluggy Connect (RF-010)",
)
async def create_connect_token(
    user_id: UUID = Depends(get_current_user_id),
    pluggy_client: PluggyClient = Depends(get_pluggy_client),
) -> ConnectTokenResponse:
    use_case = CreateConnectTokenUseCase(pluggy_client)
    result = await use_case.execute(user_id)
    return ConnectTokenResponse(
        connect_token=result.connect_token,
        access_token=result.access_token,
    )


@router.post(
    "/items",
    response_model=PluggyItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra novo Item de conexão bancária concluído no widget (RF-011/012)",
)
async def register_item(
    body: CreateItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    item_repo: PluggyItemRepository = Depends(get_pluggy_item_repository),
    pluggy_client: PluggyClient = Depends(get_pluggy_client),
    sync_log_repo: SyncLogRepository = Depends(get_sync_log_repository),
) -> PluggyItemResponse:
    use_case = RegisterPluggyItemUseCase(
        item_repo=item_repo,
        pluggy_client=pluggy_client,
        sync_log_repo=sync_log_repo,
    )
    result = await use_case.execute(
        RegisterItemInputDto(
            user_id=user_id,
            item_id=body.item_id,
            connector_id=body.connector_id,
            connector_name=body.connector_name,
        )
    )
    return PluggyItemResponse.model_validate(result)


@router.get(
    "/items",
    response_model=list[PluggyItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista conexões bancárias do usuário (RF-013)",
)
async def list_items(
    user_id: UUID = Depends(get_current_user_id),
    item_repo: PluggyItemRepository = Depends(get_pluggy_item_repository),
) -> list[PluggyItemResponse]:
    items = await item_repo.list_by_user_id(user_id)
    return [PluggyItemResponse.model_validate(item) for item in items]
