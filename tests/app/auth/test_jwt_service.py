import datetime
import uuid

import pytest

from app.auth.jwt_service import JwtService, JwtInvalid, JwtExpired

SECRET = "test-secret"


@pytest.fixture
def jwt_service():
    return JwtService(secret=SECRET)


def test_create_and_validate_token(jwt_service):
    # Create token
    last_logged_in = datetime.datetime.now(datetime.UTC).isoformat()
    user_id = uuid.uuid4().hex
    content = {"user_id": user_id, "last_logged_in": last_logged_in}
    token, expires_at = jwt_service.create_token(content=content, expires_in=60)

    assert isinstance(token, str)

    # Validate token
    decoded = jwt_service.validate_token(token)
    assert decoded["user_id"] == user_id
    assert decoded["last_logged_in"] == last_logged_in
    assert "iat" in decoded
    assert "exp" in decoded


def test_expired_token(jwt_service, monkeypatch):
    content = {"user_id": 1}
    now = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=120)
    token, expires_at = jwt_service.create_token(
        content=content, expires_in=60, now=now
    )
    with pytest.raises(JwtExpired):
        jwt_service.validate_token(token)


def test_invalid_token(jwt_service):
    with pytest.raises(JwtInvalid):
        jwt_service.validate_token("this.is.not.a.token")
