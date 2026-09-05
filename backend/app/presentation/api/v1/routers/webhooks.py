from typing import Any

from fastapi import APIRouter, Depends, Path, status

from app.application.use_cases.pluggy.process_webhook import (
    ProcessPluggyWebhookUseCase,
)
from app.core.config import settings
from app.domain.repositories.pluggy_item_repository import PluggyItemRepository
from app.domain.repositories.sync_log_repository import SyncLogRepository
from app.presentation.api.v1.schemas.pluggy import WebhookResponse
from app.presentation.dependencies import (
    get_pluggy_item_repository,
    get_sync_log_repository,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/pluggy/{secret}",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Endpoint receptor seguro de notificações webhook da Pluggy (Seção 7.7)",
)
async def handle_pluggy_webhook(
    payload: dict[str, Any],
    secret: str = Path(
        ..., description="Segredo embutido no path para validação constante de tempo"
    ),
    item_repo: PluggyItemRepository = Depends(get_pluggy_item_repository),
    sync_log_repo: SyncLogRepository = Depends(get_sync_log_repository),
) -> WebhookResponse:
    use_case = ProcessPluggyWebhookUseCase(
        item_repo=item_repo,
        sync_log_repo=sync_log_repo,
        expected_secret=settings.PLUGGY_WEBHOOK_SECRET,
    )
    result = await use_case.execute(secret, payload)
    return WebhookResponse(received=result.get("received", True))
