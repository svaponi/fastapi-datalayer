import datetime
import sys
import uuid

import fastapi
import pydantic
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class ChatMessageTable(Base):
    __tablename__ = "chat_message"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint("chat_message_id", name="chat_message_pkey"),
    )
    chat_message_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    chat_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    from_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    entered_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime, server_default=sqlalchemy.text("now()")
    )
    content: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )


ChatMessageRecord = ChatMessageTable


class ChatMessageRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_id: uuid.UUID
    from_user_id: uuid.UUID
    entered_at: datetime.datetime = datetime.datetime.now()
    content: str | None = None


class ChatMessageRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_id: uuid.UUID | None = None
    from_user_id: uuid.UUID | None = None
    entered_at: datetime.datetime | None = None
    content: str | None = None


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


class ChatMessageRepository(BaseRepository[ChatMessageRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, ChatMessageRecord)

    ### custom methods go below ###
