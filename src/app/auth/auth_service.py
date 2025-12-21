import datetime
import logging
import uuid

import fastapi
import pydantic

from app.auth.jwt_service import JwtService
from app.auth.utils import hash_password, verify_hashed_password
from app.core.errors import UnauthorizedException
from app.datalayer.auth_user_repository import (
    AuthUserRepository,
    AuthUserRecordInsert,
    AuthUserRecord,
)


class AccessTokenDto(pydantic.BaseModel):
    user_id: uuid.UUID
    expires_at: datetime.datetime
    access_token: str


class AuthUserDto(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    email_verified: bool = False
    full_name: str | None = None


class AuthService:
    def __init__(
        self,
        auth_user_repo: AuthUserRepository = fastapi.Depends(),
        jwt_service: JwtService = fastapi.Depends(),
    ) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{self.__module__}.{type(self).__name__}")
        self.auth_user_repo = auth_user_repo
        self.jwt_service = jwt_service
        self.jwt_ttl = 300

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> uuid.UUID:
        auth_user_id = await self.auth_user_repo.insert(
            AuthUserRecordInsert(
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
            )
        )
        return auth_user_id

    async def _get_user_by_credentials(
        self,
        email: str,
        password: str,
    ) -> AuthUserRecord | None:
        auth_user = await self.auth_user_repo.find_by_email(
            email=email,
        )
        if not auth_user:
            return None
        hashed_password = auth_user.hashed_password
        if not hashed_password:
            return None
        ok = verify_hashed_password(password, hashed_password)
        if not ok:
            return None
        return auth_user

    async def get_user_by_token(
        self,
        token: str,
    ) -> tuple[AuthUserDto, datetime.datetime]:
        try:
            verified = self.jwt_service.validate_token(token)
            auth_user_id = uuid.UUID(hex=verified["sub"])
            expires_at = datetime.datetime.fromtimestamp(
                verified["exp"], tz=datetime.UTC
            )
        except Exception as e:
            raise UnauthorizedException() from e
        auth_user = await self.auth_user_repo.get_or_none_by_id(auth_user_id)
        if not auth_user:
            raise UnauthorizedException()
        dto = AuthUserDto(
            user_id=auth_user.auth_user_id,
            email_verified=auth_user.email_verified,
            email=auth_user.email,
            full_name=auth_user.full_name,
        )
        return dto, expires_at

    async def login_by_credentials(
        self,
        email: str,
        password: str,
    ) -> AccessTokenDto:
        auth_user = await self._get_user_by_credentials(
            email=email,
            password=password,
        )
        if not auth_user:
            raise UnauthorizedException()
        access_token, expires_at = self.jwt_service.create_token(
            content=dict(sub=auth_user.auth_user_id.hex),
            expires_in=self.jwt_ttl,
        )
        return AccessTokenDto(
            user_id=auth_user.auth_user_id,
            expires_at=expires_at,
            access_token=access_token,
        )
