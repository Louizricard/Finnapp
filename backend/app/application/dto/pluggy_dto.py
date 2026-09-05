from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ConnectTokenOutputDto:
    access_token: str
    connect_token: str


@dataclass(frozen=True)
class RegisterItemInputDto:
    user_id: UUID
    item_id: str
    connector_id: int | None = None
    connector_name: str | None = None


@dataclass(frozen=True)
class PluggyItemOutputDto:
    id: UUID
    user_id: UUID
    pluggy_item_id: str
    connector_id: int | None
    connector_name: str | None
    status: str
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ProcessWebhookInputDto:
    secret: str
    payload: dict[str, Any]
