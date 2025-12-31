import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _UserAuthTable(Base):
    __tablename__ = "user_auth"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint("user_auth_id", name="user_auth_pkey"),
    )
    user_auth_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    user_type: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    agency_id: sqlalchemy.orm.Mapped[uuid.UUID | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    permissions: sqlalchemy.orm.Mapped[list[str] | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ARRAY(sqlalchemy.String)
    )


UserAuthRecord = _UserAuthTable


class UserAuthRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    user_auth_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    user_type: str
    agency_id: uuid.UUID | None = None
    permissions: list[str] | None = None


class UserAuthRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    user_id: uuid.UUID | None = None
    user_type: str | None = None
    agency_id: uuid.UUID | None = None
    permissions: list[str] | None = None


class UserAuthRepository(BaseRepository[UserAuthRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, UserAuthRecord)

    ### custom methods go below ###
