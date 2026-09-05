import httpx
import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_flow(async_client: httpx.AsyncClient) -> None:
    # 1. Reject invalid setup_token
    res_wrong_setup = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123!",
            "full_name": "Usuário Teste",
            "setup_token": "wrong-token",
        },
    )
    assert res_wrong_setup.status_code == 403
    data_wrong = res_wrong_setup.json()
    assert data_wrong["title"] == "Acesso negado"

    # 2. Successfully register single user with valid setup_token
    res_success = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "Password123!",
            "full_name": "Usuário Teste",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    assert res_success.status_code == 201
    data = res_success.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "user@example.com"
    assert data["user"]["full_name"] == "Usuário Teste"

    # 3. Reject second registration (single user enforcement)
    res_second = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "second@example.com",
            "password": "Password123!",
            "full_name": "Segundo Usuário",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    assert res_second.status_code == 409
    assert res_second.json()["title"] == "Conflito de dados"


@pytest.mark.asyncio
async def test_login_flow(async_client: httpx.AsyncClient) -> None:
    # Setup user
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123!",
            "full_name": "Login Test",
            "setup_token": settings.SETUP_TOKEN,
        },
    )

    # 1. Invalid password
    res_wrong_pw = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "WrongPassword!"},
    )
    assert res_wrong_pw.status_code == 401

    # 2. Valid login
    res_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Password123!"},
    )
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data


@pytest.mark.asyncio
async def test_get_me_flow(async_client: httpx.AsyncClient) -> None:
    # 1. Unauthorized without token
    res_no_auth = await async_client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401

    # 2. Register and authenticate
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "Password123!",
            "full_name": "Perfil Teste",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    token = reg.json()["access_token"]

    # 3. Authorized /auth/me
    res_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == "me@example.com"
    assert me_data["full_name"] == "Perfil Teste"


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_reuse_prevention(
    async_client: httpx.AsyncClient,
) -> None:
    # Register
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "rotate@example.com",
            "password": "Password123!",
            "full_name": "Rotation Test",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    token_v1 = reg.json()["refresh_token"]

    # Refresh token rotation (exchange token_v1 for token_v2)
    res_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_v1},
    )
    assert res_refresh.status_code == 200
    data_v2 = res_refresh.json()
    token_v2 = data_v2["refresh_token"]
    assert token_v2 != token_v1

    # Verify new access_token works
    res_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data_v2['access_token']}"},
    )
    assert res_me.status_code == 200

    # Reuse old token_v1 (replay attack): must be rejected
    res_replay = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_v1},
    )
    assert res_replay.status_code == 401


@pytest.mark.asyncio
async def test_logout_flow(async_client: httpx.AsyncClient) -> None:
    # Register
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout@example.com",
            "password": "Password123!",
            "full_name": "Logout Test",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    refresh_token = reg.json()["refresh_token"]

    # Logout
    res_logout = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert res_logout.status_code == 200
    assert res_logout.json()["status"] == "ok"

    # Refresh with logged out token must fail
    res_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert res_refresh.status_code == 401


@pytest.mark.asyncio
async def test_web_cookie_support(async_client: httpx.AsyncClient) -> None:
    # Register with X-Client-Platform: web
    res_reg = await async_client.post(
        "/api/v1/auth/register",
        headers={"X-Client-Platform": "web"},
        json={
            "email": "web@example.com",
            "password": "Password123!",
            "full_name": "Web User",
            "setup_token": settings.SETUP_TOKEN,
        },
    )
    assert res_reg.status_code == 201
    assert "finapp_refresh_token" in res_reg.cookies

    cookie_val = res_reg.cookies["finapp_refresh_token"]

    # Refresh using cookie without body
    res_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        headers={
            "X-Client-Platform": "web",
            "Cookie": f"finapp_refresh_token={cookie_val}",
        },
    )
    assert res_refresh.status_code == 200
    assert "access_token" in res_refresh.json()
    assert "finapp_refresh_token" in res_refresh.cookies
