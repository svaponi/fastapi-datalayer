import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _ChatMessageToUserTable(Base):
    __tablename__ = "chat_message_to_user"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(
            "chat_message_to_user_id", name="chat_message_to_user_pkey"
        ),
    )
    chat_message_to_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.Uuid,
            primary_key=True,
            server_default=sqlalchemy.text("uuid_generate_v4()"),
        )
    )
    chat_message_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    to_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    read_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.DateTime)
    )


ChatMessageToUserRecord = _ChatMessageToUserTable


class ChatMessageToUserRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_to_user_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_message_id: uuid.UUID
    to_user_id: uuid.UUID
    read_at: datetime.datetime | None = None


class ChatMessageToUserRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_id: uuid.UUID | None = None
    to_user_id: uuid.UUID | None = None
    read_at: datetime.datetime | None = None


class ChatMessageToUserRepository(BaseRepository[ChatMessageToUserRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, ChatMessageToUserRecord)

    ### custom methods go below ###
