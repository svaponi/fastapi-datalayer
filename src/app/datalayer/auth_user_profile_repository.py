import sys
import uuid


import fastapi

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class AuthUserProfileTable(Base):
    __tablename__ = "auth_user_profile"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(
            "auth_user_profile_id", name="auth_user_profile_pkey"
        ),
    )
    auth_user_profile_id: sqlalchemy.orm.Mapped[uuid.UUID] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.Uuid,
            primary_key=True,
            server_default=sqlalchemy.text("uuid_generate_v4()"),
        )
    )
    auth_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    auth_user_profile_type: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    agency_id: sqlalchemy.orm.Mapped[uuid.UUID | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    permissions: sqlalchemy.orm.Mapped[list[str]] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ARRAY(sqlalchemy.String),
        server_default=sqlalchemy.text("ARRAY[]::character varying[]"),
    )


AuthUserProfileRecord = AuthUserProfileTable


class AuthUserProfileRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_profile_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    auth_user_id: uuid.UUID
    auth_user_profile_type: str
    agency_id: uuid.UUID | None = None
    permissions: list[str] = pydantic.Field(default_factory=list)


class AuthUserProfileRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_id: uuid.UUID | None = None
    auth_user_profile_type: str | None = None
    agency_id: uuid.UUID | None = None
    permissions: list[str] | None = None


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


class AuthUserProfileRepository(BaseRepository[AuthUserProfileRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, AuthUserProfileRecord)

    ### custom methods go below ###
