import pytest

from app.auth.auth_service import AuthService, UserType
from app.auth.jwt_service import JwtService
from app.auth.user_auth_service import UserAuthService
from app.auth.user_service import UserService


@pytest.fixture
def jwt_service():
    return JwtService("secret-key")


@pytest.mark.asyncio
async def test_create_user_and_login(facade, jwt_service):
    user_service = UserService(facade)
    user_auth_service = UserAuthService(facade)
    auth_service = AuthService(
        facade=facade,
        user_service=user_service,
        user_auth_service=user_auth_service,
        jwt_service=jwt_service,
    )
    user_id = await auth_service.create_user(
        email="sam@example.com",
        password="secret",
        user_type=UserType.tenant,
    )
    user = await user_service.get_user_by_credentials(
        email="sam@example.com",
        password="wrong password",
    )
    assert user is None
    user = await user_service.get_user_by_credentials(
        email="sam@example.com",
        password="secret",
    )
    assert user.user_id == user_id
    auth = await auth_service.login_by_credentials(
        email="sam@example.com",
        password="secret",
    )
    assert auth.user.user_id == user_id
    decoded = jwt_service.validate_token(auth.access_token)
    assert decoded["sub"] == user_id.hex
