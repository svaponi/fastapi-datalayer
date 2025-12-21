import datetime
import re

import fastapi
from fastapi.security import APIKeyHeader

from app.auth.auth_service import AuthService, AuthUserDto
from app.core.errors import UnauthorizedException


async def require_api_key(
    _=fastapi.Depends(
        APIKeyHeader(
            name="x-api-key",
            description="Paste the api key",
            auto_error=False,
        )
    ),
) -> None:
    pass


def set_auth_cookie(
    response: fastapi.Response,
    token: str,
    expires_at: datetime.datetime,
) -> None:
    response.set_cookie(
        "authorization",
        f"bearer {token}",
        httponly=True,
        expires=expires_at,
    )


async def get_auth_user(
    request: fastapi.Request,
    response: fastapi.Response,
    auth_service: AuthService = fastapi.Depends(),
    _=fastapi.Depends(require_api_key),
) -> AuthUserDto:
    authorization = request.headers.get("authorization")
    if not authorization:
        authorization = request.cookies.get("authorization")
    if authorization and re.match(r"^bearer ", authorization, re.IGNORECASE):
        token = authorization[7:]
        auth_user, expires_at = await auth_service.get_user_by_token(token)
        if auth_user:
            set_auth_cookie(
                response,
                token=token,
                expires_at=expires_at,
            )
            return auth_user
    raise UnauthorizedException()
