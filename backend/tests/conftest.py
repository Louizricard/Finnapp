from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy import text

from app.infrastructure.db.models import Base
from app.infrastructure.db.session import async_session_factory, engine
from app.presentation.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_and_clean_tables() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE users, refresh_tokens CASCADE;"))

    yield

    await engine.dispose()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
