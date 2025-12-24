import sys
import uuid


import fastapi

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class ChatTable(Base):
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


ChatRecord = ChatTable


class ChatRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    auth_user_ids: list[uuid.UUID] = pydantic.Field(default_factory=list)


class ChatRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_ids: list[uuid.UUID] | None = None


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


class ChatRepository(BaseRepository[ChatRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, ChatRecord)

    ### custom methods go below ###
