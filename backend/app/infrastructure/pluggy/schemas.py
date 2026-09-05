from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PluggyAuthRequest(BaseModel):
    client_id: str = Field(..., alias="clientId")
    client_secret: str = Field(..., alias="clientSecret")

    model_config = ConfigDict(populate_by_name=True)


class PluggyAuthResponse(BaseModel):
    api_key: str = Field(..., alias="apiKey")

    model_config = ConfigDict(populate_by_name=True)


class PluggyConnectTokenOptions(BaseModel):
    client_user_id: str | None = Field(None, alias="clientUserId")
    webhook_url: str | None = Field(None, alias="webhookUrl")
    oauth_redirect_uri: str | None = Field(None, alias="oauthRedirectUri")
    avoid_duplicates: bool | None = Field(None, alias="avoidDuplicates")

    model_config = ConfigDict(populate_by_name=True)


class PluggyConnectTokenRequest(BaseModel):
    item_id: str | None = Field(None, alias="itemId")
    options: PluggyConnectTokenOptions | None = None

    model_config = ConfigDict(populate_by_name=True)


class PluggyConnectTokenResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")

    model_config = ConfigDict(populate_by_name=True)


class PluggyConnector(BaseModel):
    id: int
    name: str
    primary_color: str | None = Field(None, alias="primaryColor")
    institution_url: str | None = Field(None, alias="institutionUrl")
    country: str | None = None
    type: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class PluggyItemResponse(BaseModel):
    id: str
    user: str | None = None
    status: str
    execution_status: str | None = Field(None, alias="executionStatus")
    last_updated_at: datetime | None = Field(None, alias="lastUpdatedAt")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    connector: PluggyConnector | None = None
    error: dict[str, Any] | str | None = None

    model_config = ConfigDict(populate_by_name=True)


class PluggyWebhookPayload(BaseModel):
    event: str
    item_id: str = Field(..., alias="itemId")
    event_id: str | None = Field(None, alias="eventId")
    client_user_id: str | None = Field(None, alias="clientUserId")
    error: dict[str, Any] | str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")
