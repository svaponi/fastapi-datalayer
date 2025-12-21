import datetime
import typing

import pytest

from app.auth.auth_service import AuthService
from app.auth.jwt_service import JwtService
from app.datalayer.auth_user_repository import AuthUserRepository


class _JwtService:

    def validate_token(self, token: str) -> dict[str, typing.Any]:
        return {}

    def create_token(
        self, content: typing.Any, expires_in: int, now: datetime.datetime | None = None
    ) -> tuple[str, datetime.datetime]:
        return "you're good to go", datetime.datetime.now(datetime.UTC)


@pytest.fixture
def jwt_service():
    return JwtService("secret-key")


@pytest.fixture
def auth_service(db, jwt_service):
    return AuthService(auth_user_repo=AuthUserRepository(db), jwt_service=jwt_service)


@pytest.mark.asyncio
async def test_create_user_and_login(auth_service, jwt_service):
    auth_user_id = await auth_service.create_user(
        email="sam@example.com",
        password="secret",
    )
    auth_user = await auth_service._get_user_by_credentials(
        email="sam@example.com",
        password="wrong password",
    )
    assert auth_user is None
    auth_user = await auth_service._get_user_by_credentials(
        email="sam@example.com",
        password="secret",
    )
    assert auth_user.auth_user_id == auth_user_id
    dto = await auth_service.login_by_credentials(
        email="sam@example.com",
        password="secret",
    )
    assert dto.user_id == auth_user_id
    decoded = jwt_service.validate_token(dto.access_token)
    assert decoded["sub"] == auth_user_id.hex
