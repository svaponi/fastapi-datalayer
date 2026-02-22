import datetime
import logging
import uuid

import fastapi
import pydantic

from app.datalayer.facade import DatalayerFacade


class UserDto(pydantic.BaseModel):
    id: uuid.UUID
    email: str
    name: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserService:
    def __init__(
        self,
        facade: DatalayerFacade = fastapi.Depends(),
    ) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{self.__module__}.{type(self).__name__}")
        self.facade = facade

    async def get_users(self, size: int) -> list[UserDto]:
        records, _ = await self.facade.users.get_page(
            size=size,
            skip_count=True,
        )
        return [
            UserDto(
                id=r.id,
                email=r.email,
                name=r.name,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in records
        ]
