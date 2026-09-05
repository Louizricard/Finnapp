from datetime import timedelta
from uuid import uuid4

import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_jwt_access_token_creation_and_decoding() -> None:
    user_id = uuid4()
    email = "luiz@example.com"

    token = create_access_token(user_id=user_id, email=email)
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_access_token_expired() -> None:
    user_id = uuid4()
    email = "luiz@example.com"

    # Create expired token (negative delta)
    expired_token = create_access_token(
        user_id=user_id,
        email=email,
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token(expired_token)

    assert "expirado" in exc_info.value.detail.lower()


def test_jwt_invalid_token() -> None:
    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token("not.a.valid.jwt.token")

    assert "inválido" in exc_info.value.detail.lower()


def test_refresh_token_generation_and_hashing() -> None:
    raw_token_1, hash_1, expires_1 = generate_refresh_token()
    raw_token_2, hash_2, expires_2 = generate_refresh_token()

    assert len(raw_token_1) >= 48
    assert raw_token_1 != raw_token_2
    assert hash_1 != hash_2

    # Deterministic hashing test
    assert hash_refresh_token(raw_token_1) == hash_1
    assert hash_refresh_token(raw_token_2) == hash_2
    assert expires_1 > expires_1 - timedelta(days=1)
