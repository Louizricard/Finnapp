from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConnectTokenResponse(BaseModel):
    connect_token: str
    access_token: str

    model_config = ConfigDict(from_attributes=True)


class CreateItemRequest(BaseModel):
    item_id: str = Field(
        ..., min_length=1, description="ID do Item retornado pelo widget Pluggy Connect"
    )
    connector_id: int | None = Field(
        None, description="ID do conector (ex.: Banco Inter = 201)"
    )
    connector_name: str | None = Field(
        None, description="Nome da instituição (ex.: Banco Inter)"
    )


class PluggyItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    pluggy_item_id: str
    connector_id: int | None
    connector_name: str | None
    status: str
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookResponse(BaseModel):
    received: bool = True
