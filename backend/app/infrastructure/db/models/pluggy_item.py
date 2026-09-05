from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.sync_log import SyncLogModel
    from app.infrastructure.db.models.user import UserModel


class PluggyItemModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pluggy_items"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pluggy_item_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    connector_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    connector_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UPDATING",
        index=True,
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="pluggy_items",
    )
    sync_logs: Mapped[list["SyncLogModel"]] = relationship(
        "SyncLogModel",
        back_populates="pluggy_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
