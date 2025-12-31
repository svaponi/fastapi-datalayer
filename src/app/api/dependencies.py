import datetime
import re

import fastapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.auth_service import AuthService, AuthDto
from app.core.errors import UnauthorizedException

security = HTTPBearer(
    description="Access token",
    auto_error=False,
)


def set_auth_cookie(
    response: fastapi.Response,
    token: str | None,
    expires_at: datetime.datetime | None = None,
) -> None:
    if token:
        response.set_cookie(
            "bearer",
            token,
            httponly=True,
            expires=expires_at,
        )
    else:
        response.delete_cookie("bearer")


async def get_auth(
    request: fastapi.Request,
    response: fastapi.Response,
    auth_service: AuthService = fastapi.Depends(),
    credentials: HTTPAuthorizationCredentials = fastapi.Depends(security),
) -> AuthDto:
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        authorization = request.headers.get("authorization")
        if authorization and re.match(r"^bearer ", authorization, re.IGNORECASE):
            token = authorization[7:]
    if not token:
        token = request.cookies.get("bearer")
    if token:
        auth = await auth_service.get_user_by_token(token)
        if auth:
            set_auth_cookie(
                response,
                token=token,
                expires_at=auth.expires_at,
            )
            return auth
    set_auth_cookie(
        response,
        token=None,
    )
    raise UnauthorizedException()
