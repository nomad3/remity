import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt

from app.core import security
from app.core.config import settings

def test_password_hashing():
    """ Test password hashing and verification. """
    password = "testpassword123"
    hashed_password = security.get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > len(password)
    # Check that the hash itself doesn't contain the password
    assert password not in hashed_password
    # Verify correct password
    assert security.verify_password(password, hashed_password)
    # Verify incorrect password
    assert not security.verify_password("wrongpassword", hashed_password)

def test_create_access_token():
    """ Test access token creation and basic payload. """
    subject = "test@example.com"
    token = security.create_access_token(subject)
    assert isinstance(token, str)
    # Decode manually to check claims beyond what decode_token validates
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == subject
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()

def test_create_refresh_token():
    """ Test refresh token creation and type claim. """
    subject = "test@example.com"
    token = security.create_refresh_token(subject)
    assert isinstance(token, str)
    # Decode manually to check claims
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == subject
    assert payload.get("type") == "refresh" # Check for refresh token type claim
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()

def test_token_expiry():
    """ Test token expiry calculation and verification. """
    subject = "test@example.com"
    # Test default expiry
    token_default = security.create_access_token(subject)
    payload_default = jwt.decode(token_default, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    expected_expiry_default = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs(payload_default["exp"] - expected_expiry_default.timestamp()) < 5 # Allow 5s difference

    # Test custom expiry
    custom_delta = timedelta(hours=1)
    token_custom = security.create_access_token(subject, expires_delta=custom_delta)
    payload_custom = jwt.decode(token_custom, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    expected_expiry_custom = datetime.now(timezone.utc) + custom_delta
    assert abs(payload_custom["exp"] - expected_expiry_custom.timestamp()) < 5 # Allow 5s difference

def test_decode_token_valid():
    """ Test decoding a valid token. """
    subject = "validuser@test.com"
    token = security.create_access_token(subject)
    payload = security.decode_token(token)
    assert payload is not None
    assert payload.sub == subject

def test_decode_token_invalid_signature():
    """ Test decoding a token with an invalid signature. """
    subject = "user@test.com"
    token = security.create_access_token(subject)
    # Tamper with the token slightly
    tampered_token = token[:-1] + ('a' if token[-1] != 'a' else 'b')
    payload = security.decode_token(tampered_token)
    assert payload is None

def test_decode_token_expired():
    """ Test decoding an expired token. """
    subject = "user@test.com"
    # Create a token that expired 1 second ago
    expired_delta = timedelta(seconds=-1)
    token = security.create_access_token(subject, expires_delta=expired_delta)
    payload = security.decode_token(token)
    assert payload is None # decode_token should return None for expired tokens

def test_verify_refresh_token_valid():
    """ Test verifying a valid refresh token. """
    subject = "refresh@test.com"
    token = security.create_refresh_token(subject)
    payload = security.verify_refresh_token(token)
    assert payload is not None
    assert payload.sub == subject

def test_verify_refresh_token_invalid_type():
    """ Test verifying an access token as a refresh token (should fail). """
    subject = "access@test.com"
    token = security.create_access_token(subject) # Create an access token (no 'type' claim)
    payload = security.verify_refresh_token(token)
    assert payload is None
