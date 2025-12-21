import datetime
import uuid

import fastapi
import pydantic

from app.auth.auth_service import AuthService, AuthUserDto
from app.auth.dependencies import get_auth_user, set_auth_cookie

router = fastapi.APIRouter()


class SignupRequest(pydantic.BaseModel):
    email: str
    password: str
    full_name: str | None = None


class SignupResponse(pydantic.BaseModel):
    user_id: uuid.UUID


@router.post("/signup")
async def signup(
    payload: SignupRequest = fastapi.Body(...),
    auth_service: AuthService = fastapi.Depends(),
) -> SignupResponse:
    user_id = await auth_service.create_user(
        payload.email,
        payload.password,
        payload.full_name,
    )
    return SignupResponse(
        user_id=user_id,
    )


class LoginRequest(pydantic.BaseModel):
    email: str
    password: str


class LoginResponse(pydantic.BaseModel):
    user_id: uuid.UUID
    expires_at: datetime.datetime
    access_token: str


@router.post("/login")
async def login(
    response: fastapi.Response,
    payload: LoginRequest = fastapi.Body(...),
    auth_service: AuthService = fastapi.Depends(),
) -> LoginResponse:
    dto = await auth_service.login_by_credentials(payload.email, payload.password)
    set_auth_cookie(
        response,
        token=dto.access_token,
        expires_at=dto.expires_at,
    )
    return LoginResponse(
        user_id=dto.user_id,
        expires_at=dto.expires_at,
        access_token=dto.access_token,
    )


class WhoamiResponse(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None


@router.get("/whoami")
async def whoami(
    auth_user: AuthUserDto = fastapi.Depends(get_auth_user),
) -> WhoamiResponse:
    return WhoamiResponse(
        user_id=auth_user.user_id,
        email=auth_user.email,
        full_name=auth_user.full_name,
    )
