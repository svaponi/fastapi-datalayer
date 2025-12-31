import datetime
import logging
import uuid

import fastapi
import pydantic

from app.auth.jwt_service import JwtService
from app.auth.user_auth_service import UserAuthService, UserType, UserAuthDto
from app.auth.user_service import UserService, UserDto
from app.core.errors import UnauthorizedException
from app.datalayer.facade import DatalayerFacade

_logger = logging.getLogger(__name__)


class AuthDto(pydantic.BaseModel):
    user: UserDto
    auths: list[UserAuthDto]
    expires_at: datetime.datetime
    access_token: str


class AuthService:
    def __init__(
        self,
        facade: DatalayerFacade = fastapi.Depends(),
        user_service: UserService = fastapi.Depends(),
        user_auth_service: UserAuthService = fastapi.Depends(),
        jwt_service: JwtService = fastapi.Depends(),
    ) -> None:
        super().__init__()
        self.facade = facade
        self.user_service = user_service
        self.user_auth_service = user_auth_service
        self.jwt_service = jwt_service
        self.jwt_ttl = 3600

    async def create_user(
        self,
        email: str,
        password: str,
        user_type: UserType,
        full_name: str | None = None,
    ) -> uuid.UUID:
        async with self.facade.db.get_session() as session:
            user_id = await self.user_service.create_user(
                email=email,
                password=password,
                full_name=full_name,
                reuse_session=session,
            )
            await self.user_auth_service.add_user_auth(
                user_id=user_id,
                user_type=user_type,
                reuse_session=session,
            )
        return user_id

    async def get_user_by_token(
        self,
        token: str,
    ) -> AuthDto:
        try:
            verified = self.jwt_service.validate_token(token)
            user_id = uuid.UUID(hex=verified["sub"])
            expires_at = datetime.datetime.fromtimestamp(
                verified["exp"], tz=datetime.UTC
            )
        except Exception as e:
            raise UnauthorizedException() from e
        user = await self.user_service.get_or_none_by_id(user_id)
        if not user:
            raise UnauthorizedException()
        auths = await self.user_auth_service.get_user_auths_by_user_id(
            user_id=user_id,
        )
        dto = AuthDto(
            user=user,
            auths=auths,
            expires_at=expires_at,
            access_token=token,
        )
        return dto

    async def login_by_credentials(
        self,
        email: str,
        password: str,
    ) -> AuthDto:
        user = await self.user_service.get_user_by_credentials(
            email=email,
            password=password,
        )
        if not user:
            raise UnauthorizedException()
        access_token, expires_at = self.jwt_service.create_token(
            content=dict(sub=user.user_id.hex),
            expires_in=self.jwt_ttl,
        )
        auths = await self.user_auth_service.get_user_auths_by_user_id(
            user_id=user.user_id,
        )
        return AuthDto(
            user=user,
            auths=auths,
            expires_at=expires_at,
            access_token=access_token,
        )
