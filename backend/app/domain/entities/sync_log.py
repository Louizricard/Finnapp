from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class SyncLog:
    event_type: str
    status: str
    payload: dict[str, Any]
    pluggy_item_id: UUID | None = None
    error_message: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
