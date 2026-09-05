from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class PluggyItem:
    user_id: UUID
    pluggy_item_id: str
    connector_id: int | None = None
    connector_name: str | None = None
    status: str = "UPDATING"
    last_synced_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
