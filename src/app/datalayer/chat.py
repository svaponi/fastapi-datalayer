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
    chat_title: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    user_ids: sqlalchemy.orm.Mapped[list[uuid.UUID] | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.ARRAY(sqlalchemy.Uuid))
    )


ChatRecord = _ChatTable


class ChatRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_title: str | None = None
    user_ids: list[uuid.UUID] | None = None


class ChatRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_title: str | None = None
    user_ids: list[uuid.UUID] | None = None


class ChatRepository(BaseRepository[ChatRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, ChatRecord)

    ### custom methods go below ###
