import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification"""
    password = "securepassword123"
    hashed = get_password_hash(password)

    assert hashed != password  # Should be hashed
    assert verify_password(password, hashed)  # Should verify correctly
    assert not verify_password("wrongpassword", hashed)  # Wrong password fails


def test_create_and_decode_token():
    """Test JWT token creation and decoding"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_token_with_expiration():
    """Test token with custom expiration"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires_delta)

    decoded = decode_access_token(token)
    assert decoded is not None


def test_invalid_token():
    """Test decoding an invalid token"""
    invalid_token = "this.is.invalid"
    decoded = decode_access_token(invalid_token)
    assert decoded is None
