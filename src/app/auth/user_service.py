import logging
import typing
import uuid

import fastapi
import pydantic
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import hash_password, verify_hashed_password
from app.datalayer.facade import DatalayerFacade
from app.datalayer.user_account import UserAccountRecordInsert


class UserDto(pydantic.BaseModel):
    user_id: uuid.UUID
    email: str
    email_verified: bool = False
    full_name: str | None = None


class UserService:
    def __init__(
        self,
        facade: DatalayerFacade = fastapi.Depends(),
    ) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{self.__module__}.{type(self).__name__}")
        self.facade = facade

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
        reuse_session: AsyncSession = None,
    ) -> uuid.UUID:
        user_id = await self.facade.user_account.insert(
            UserAccountRecordInsert(
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
            ),
            reuse_session=reuse_session,
        )
        return user_id

    async def get_user_by_credentials(
        self,
        email: str,
        password: str,
    ) -> UserDto | None:
        user = await self.facade.user_account.find_by_email(
            email=email,
        )
        if not user:
            return None
        hashed_password = user.hashed_password
        if not hashed_password:
            return None
        ok = verify_hashed_password(password, hashed_password)
        if not ok:
            return None
        return UserDto(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
        )

    async def get_or_none_by_id(
        self,
        user_id: uuid.UUID,
    ) -> UserDto | None:
        user = await self.facade.user_account.get_or_none_by_id(user_id)
        if not user:
            return None
        return UserDto(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
        )

    async def get_display_name_by_ids(
        self,
        user_ids: typing.Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, str]:
        by_id = await self.facade.user_account.get_by_ids(set(user_ids))
        return {user.user_id: user.full_name or user.email for user in by_id.values()}

    async def get_distinct_emails(
        self,
    ) -> list[str]:
        return await self.facade.user_account.get_distinct_emails()
