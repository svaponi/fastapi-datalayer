import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _AuthUserTable(Base):
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


AuthUserRecord = _AuthUserTable


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


class AuthUserRepository(BaseRepository[AuthUserRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, AuthUserRecord)

    ### custom methods go below ###

    async def find_by_email(
        self,
        email: str,
        filters: dict | None = None,
    ) -> AuthUserRecord | None:
        query = sqlalchemy.select(_AuthUserTable).where(
            _AuthUserTable.email == email,
        )
        query = self._with_filters(query, filters)
        async with self.db.get_session(readonly=True) as session:
            response = await session.execute(query)
            result = response.scalar_one_or_none()
        return result
