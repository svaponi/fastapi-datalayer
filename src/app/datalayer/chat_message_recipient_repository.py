import datetime
import sys
import uuid

import fastapi
import pydantic
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class ChatMessageRecipientTable(Base):
    __tablename__ = "chat_message_recipient"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(
            "chat_message_recipient_id", name="chat_message_recipient_pkey"
        ),
    )
    chat_message_recipient_id: sqlalchemy.orm.Mapped[uuid.UUID] = (
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
    to_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    entered_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime, server_default=sqlalchemy.text("now()")
    )
    notified_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.DateTime)
    )
    sent_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.DateTime)
    )
    read_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.DateTime)
    )


ChatMessageRecipientRecord = ChatMessageRecipientTable


class ChatMessageRecipientRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_recipient_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_message_id: uuid.UUID
    chat_id: uuid.UUID
    to_user_id: uuid.UUID
    entered_at: datetime.datetime = datetime.datetime.now()
    notified_at: datetime.datetime | None = None
    sent_at: datetime.datetime | None = None
    read_at: datetime.datetime | None = None


class ChatMessageRecipientRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_id: uuid.UUID | None = None
    chat_id: uuid.UUID | None = None
    to_user_id: uuid.UUID | None = None
    entered_at: datetime.datetime | None = None
    notified_at: datetime.datetime | None = None
    sent_at: datetime.datetime | None = None
    read_at: datetime.datetime | None = None


def get_db(request: fastapi.Request) -> DB:
    if not hasattr(request.app.state, "db"):
        message = """DB not found in app.state.
        Make sure to initialize the DB in your FastAPI app like this:

        ```
        import os
        import fastapi
        from asyncpg_datalayer.db_factory import create_db

        app = fastapi.FastAPI()
        app.state.db = create_db()
        ```
        """
        print(message, file=sys.stderr)
        raise RuntimeError("DB not found in app.state")
    return request.app.state.db


class ChatMessageRecipientRepository(BaseRepository[ChatMessageRecipientRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, ChatMessageRecipientRecord)

    ### custom methods go below ###
