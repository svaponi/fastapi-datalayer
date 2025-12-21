import sys
import uuid


import fastapi

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class AuthUserTable(Base):
    __tablename__ = "auth_user"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint("auth_user_id", name="auth_user_pkey"),
    )
    auth_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    email: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(sqlalchemy.String)
    email_verified: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Boolean, server_default=sqlalchemy.text("false")
    )
    hashed_password: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    full_name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )


AuthUserRecord = AuthUserTable


class AuthUserRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    email: str
    email_verified: bool = False
    hashed_password: str | None = None
    full_name: str | None = None


class AuthUserRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    email: str | None = None
    email_verified: bool | None = None
    hashed_password: str | None = None
    full_name: str | None = None


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


class AuthUserRepository(BaseRepository[AuthUserRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, AuthUserRecord)

    ### custom methods go below ###

    async def find_by_email(
        self,
        email: str,
        filters: dict | None = None,
    ) -> AuthUserRecord | None:
        query = sqlalchemy.select(AuthUserTable).where(
            AuthUserTable.email == email,
        )
        query = self._with_filters(query, filters)
        async with self.db.get_session(readonly=True) as session:
            response = await session.execute(query)
            result = response.scalar_one_or_none()
        return result
