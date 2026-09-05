import secrets
from typing import Any

from app.core.exceptions import UnauthorizedException
from app.core.logging import get_logger
from app.domain.entities.sync_log import SyncLog
from app.domain.repositories.pluggy_item_repository import PluggyItemRepository
from app.domain.repositories.sync_log_repository import SyncLogRepository

logger = get_logger("pluggy_webhook")


class ProcessPluggyWebhookUseCase:
    """Caso de uso para validação e auditoria de webhooks da Pluggy (Seção 7.7 e Sprint 2)."""

    def __init__(
        self,
        item_repo: PluggyItemRepository,
        sync_log_repo: SyncLogRepository,
        expected_secret: str,
    ) -> None:
        self.item_repo = item_repo
        self.sync_log_repo = sync_log_repo
        self.expected_secret = expected_secret

    async def execute(self, secret: str, payload: dict[str, Any]) -> dict[str, bool]:
        # Validação constante de tempo do segredo no path (mitigação contra timing attacks)
        if not secrets.compare_digest(secret, self.expected_secret):
            logger.warning("invalid_webhook_secret_attempt")
            raise UnauthorizedException("Webhook secret inválido")

        event = str(payload.get("event", "unknown"))
        item_id = payload.get("itemId")
        error_info = payload.get("error")
        log_status = "ERROR" if event == "item/error" or error_info else "SUCCESS"

        logger.info("received_pluggy_webhook", webhook_event=event, item_id=item_id)

        pluggy_item_fk = None
        if item_id and isinstance(item_id, str):
            item = await self.item_repo.get_by_pluggy_item_id(item_id)
            if item:
                pluggy_item_fk = item.id
                # Atualização preliminar de status de ciclo de vida
                if event in ("item/updated", "item/created"):
                    item.status = "UPDATED"
                    await self.item_repo.update(item)
                elif event == "item/error":
                    item.status = "ERROR"
                    await self.item_repo.update(item)
                elif event == "item/waiting_user_input":
                    item.status = "WAITING_USER_INPUT"
                    await self.item_repo.update(item)

        # Auditoria obrigatória em sync_logs
        await self.sync_log_repo.create(
            SyncLog(
                pluggy_item_id=pluggy_item_fk,
                event_type=event,
                status=log_status,
                payload=payload,
                error_message=str(error_info) if error_info else None,
            )
        )

        return {"received": True}
