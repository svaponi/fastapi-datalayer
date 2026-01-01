import datetime
import uuid

import fastapi
import pydantic
from fastapi.openapi.models import Example

from app.api.dependencies import get_auth, set_auth_cookie
from app.auth.auth_service import AuthService, Auth
from app.auth.user_auth_service import UserType

router = fastapi.APIRouter()


class AuthProfileDto(pydantic.BaseModel):
    user_type: UserType
    agency_id: uuid.UUID | None = None


class AuthDto(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    profiles: list[AuthProfileDto] = []
    expires_at: datetime.datetime
    access_token: str


def _build_dto(auth: Auth) -> AuthDto:
    return AuthDto(
        user_id=auth.user.user_id,
        email=auth.user.email,
        full_name=auth.user.full_name,
        expires_at=auth.expires_at,
        access_token=auth.access_token,
        profiles=[
            AuthProfileDto(
                user_type=auth.user_type,
                agency_id=auth.agency_id,
            )
            for auth in auth.auths
        ],
    )


class SignupRequest(pydantic.BaseModel):
    email: str
    password: str
    user_type: UserType
    full_name: str | None = None


signup_examples = dict(
    default=Example(
        value=SignupRequest(
            email="new-user@example.com",
            password="secret",
            user_type=UserType.tenant,
            full_name="New User",
        )
    )
)


@router.post("/signup")
async def signup(
    response: fastapi.Response,
    payload: SignupRequest = fastapi.Body(..., openapi_examples=signup_examples),
    auth_service: AuthService = fastapi.Depends(),
) -> AuthDto:
    auth: Auth = await auth_service.signup(
        email=payload.email,
        password=payload.password,
        user_type=payload.user_type,
        full_name=payload.full_name,
    )
    set_auth_cookie(
        response,
        token=auth.access_token,
        expires_at=auth.expires_at,
    )
    return _build_dto(auth)


class LoginRequest(pydantic.BaseModel):
    email: str
    password: str


login_examples = dict(
    default=Example(value=LoginRequest(email="jdoe@example.com", password="secret"))
)


@router.post("/login")
async def login(
    response: fastapi.Response,
    payload: LoginRequest = fastapi.Body(..., openapi_examples=login_examples),
    auth_service: AuthService = fastapi.Depends(),
) -> AuthDto:
    auth: Auth = await auth_service.get_auth_by_credentials(
        payload.email, payload.password
    )
    set_auth_cookie(
        response,
        token=auth.access_token,
        expires_at=auth.expires_at,
    )
    return _build_dto(auth)


@router.put("/logout", status_code=204, description="Removes auth cookie")
async def logout(
    response: fastapi.Response,
):
    set_auth_cookie(
        response,
        token=None,
    )


@router.post("/refresh")
async def refresh(
    response: fastapi.Response,
    auth: Auth = fastapi.Depends(get_auth),
    auth_service: AuthService = fastapi.Depends(),
) -> AuthDto:
    auth: Auth = await auth_service.get_auth_by_user_id(auth.user.user_id)
    set_auth_cookie(
        response,
        token=auth.access_token,
        expires_at=auth.expires_at,
    )
    return _build_dto(auth)


@router.get("/whoami")
async def whoami(
    auth: Auth = fastapi.Depends(get_auth),
) -> AuthDto:
    return _build_dto(auth)
