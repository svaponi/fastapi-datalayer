import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _UserDeviceTable(Base):
    __tablename__ = "user_device"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint("user_device_id", name="user_device_pkey"),
    )
    user_device_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    auth_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    subscription_info: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )


UserDeviceRecord = _UserDeviceTable


class UserDeviceRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    user_device_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    auth_user_id: uuid.UUID
    subscription_info: str | None = None


class UserDeviceRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_id: uuid.UUID | None = None
    subscription_info: str | None = None


class UserDeviceRepository(BaseRepository[UserDeviceRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, UserDeviceRecord)

    ### custom methods go below ###
