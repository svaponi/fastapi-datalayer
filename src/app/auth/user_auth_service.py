import enum
import logging
import uuid

import fastapi
import pydantic
from sqlalchemy.ext.asyncio import AsyncSession

from app.datalayer.facade import DatalayerFacade
from app.datalayer.user_auth import UserAuthRecordInsert

_logger = logging.getLogger(__name__)


class UserType(enum.StrEnum):
    sysadmin = "sysadmin"
    agency_owner = "agency_owner"
    agency_staff = "agency_staff"
    tenant = "tenant"
    technician = "technician"


class UserAuthDto(pydantic.BaseModel):
    user_id: uuid.UUID
    user_type: UserType
    agency_id: uuid.UUID | None = None
    permissions: list[str] = []


class UserAuthService:
    def __init__(
        self,
        facade: DatalayerFacade = fastapi.Depends(),
    ) -> None:
        super().__init__()
        self.facade = facade

    async def add_user_auth(
        self,
        user_id: uuid.UUID,
        user_type: UserType,
        reuse_session: AsyncSession | None = None,
    ) -> uuid.UUID:
        auth_user_id = await self.facade.user_auth.insert(
            UserAuthRecordInsert(
                user_id=user_id,
                user_type=user_type,
            ),
            reuse_session=reuse_session,
        )
        return auth_user_id

    async def get_user_auths_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> list[UserAuthDto]:
        user_auths = await self.facade.user_auth.get_all(
            filters={"user_id": user_id},
        )
        return [
            UserAuthDto(
                user_id=u.user_id,
                user_type=u.user_type,
                agency_id=u.agency_id,
                permissions=u.permissions or [],
            )
            for u in user_auths
        ]
