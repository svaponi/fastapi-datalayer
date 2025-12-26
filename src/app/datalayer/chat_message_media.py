import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _ChatMessageMediaTable(Base):
    __tablename__ = "chat_message_media"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(
            "chat_message_media_id", name="chat_message_media_pkey"
        ),
    )
    chat_message_media_id: sqlalchemy.orm.Mapped[uuid.UUID] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.Uuid,
            primary_key=True,
            server_default=sqlalchemy.text("uuid_generate_v4()"),
        )
    )
    chat_message_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    chat_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    media: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )


ChatMessageMediaRecord = _ChatMessageMediaTable


class ChatMessageMediaRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_media_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_message_id: uuid.UUID
    chat_id: uuid.UUID
    media: str | None = None


class ChatMessageMediaRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_id: uuid.UUID | None = None
    chat_id: uuid.UUID | None = None
    media: str | None = None


class ChatMessageMediaRepository(BaseRepository[ChatMessageMediaRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, ChatMessageMediaRecord)

    ### custom methods go below ###
