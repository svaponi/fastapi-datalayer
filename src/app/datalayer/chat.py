import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _ChatTable(Base):
    __tablename__ = "chat"
    __table_args__ = (sqlalchemy.PrimaryKeyConstraint("chat_id", name="chat_pkey"),)
    chat_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    auth_user_ids: sqlalchemy.orm.Mapped[list[uuid.UUID]] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.ARRAY(sqlalchemy.Uuid),
            server_default=sqlalchemy.text("ARRAY[]::uuid[]"),
        )
    )


ChatRecord = _ChatTable


class ChatRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    auth_user_ids: list[uuid.UUID] = pydantic.Field(default_factory=list)


class ChatRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_ids: list[uuid.UUID] | None = None


class ChatRepository(BaseRepository[ChatRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, ChatRecord)

    ### custom methods go below ###
