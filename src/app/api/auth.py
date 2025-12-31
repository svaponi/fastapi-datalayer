import datetime
import uuid

import fastapi
import pydantic

from app.api.dependencies import get_auth, set_auth_cookie
from app.auth.auth_service import AuthService, AuthDto
from app.auth.user_auth_service import UserType

router = fastapi.APIRouter()


class SignupRequest(pydantic.BaseModel):
    email: str
    password: str
    user_type: UserType
    full_name: str | None = None


class SignupResponse(pydantic.BaseModel):
    user_id: uuid.UUID


@router.post("/signup")
async def signup(
    payload: SignupRequest = fastapi.Body(...),
    auth_service: AuthService = fastapi.Depends(),
) -> SignupResponse:
    user_id = await auth_service.create_user(
        email=payload.email,
        password=payload.password,
        user_type=payload.user_type,
        full_name=payload.full_name,
    )
    return SignupResponse(
        user_id=user_id,
    )


class LoginRequest(pydantic.BaseModel):
    email: str
    password: str


class LoginResponseAuth(pydantic.BaseModel):
    user_type: UserType
    agency_id: uuid.UUID | None = None


class LoginResponse(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    auths: list[LoginResponseAuth] = []
    expires_at: datetime.datetime
    access_token: str


@router.post("/login")
async def login(
    response: fastapi.Response,
    payload: LoginRequest = fastapi.Body(...),
    auth_service: AuthService = fastapi.Depends(),
) -> LoginResponse:
    dto: AuthDto = await auth_service.login_by_credentials(
        payload.email, payload.password
    )
    set_auth_cookie(
        response,
        token=dto.access_token,
        expires_at=dto.expires_at,
    )
    return LoginResponse(
        user_id=dto.user.user_id,
        email=dto.user.email,
        full_name=dto.user.full_name,
        expires_at=dto.expires_at,
        access_token=dto.access_token,
        auths=[
            LoginResponseAuth(
                user_type=auth.user_type,
                agency_id=auth.agency_id,
            )
            for auth in dto.auths
        ],
    )


@router.put("/logout", status_code=204)
async def logout(
    response: fastapi.Response,
):
    set_auth_cookie(
        response,
        token=None,
    )


class WhoamiResponse(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None


@router.get("/whoami")
async def whoami(
    auth: AuthDto = fastapi.Depends(get_auth),
) -> WhoamiResponse:
    return WhoamiResponse(
        user_id=auth.user.user_id,
        email=auth.user.email,
        full_name=auth.user.full_name,
    )
