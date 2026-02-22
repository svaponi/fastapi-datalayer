import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _UsersTable(Base):
    __tablename__ = "users"
    __table_args__ = (sqlalchemy.PrimaryKeyConstraint("id", name="users_pkey"),)
    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    email: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(sqlalchemy.String)
    name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    created_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime, server_default=sqlalchemy.text("now()")
    )
    updated_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime, server_default=sqlalchemy.text("now()")
    )


UsersRecord = _UsersTable


class UsersRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    email: str
    name: str | None = None
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )


class UsersRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    email: str | None = None
    name: str | None = None
    updated_at: datetime.datetime | None = None


class UsersRepository(BaseRepository[UsersRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, UsersRecord)

    ### custom methods go below ###

    async def get_distinct_emails(
        self,
        filters: dict | None = None,
    ) -> list[str]:
        query = sqlalchemy.select(sqlalchemy.distinct(_UsersTable.email))
        query = self._with_filters(query, filters)
        async with self.db.get_session(readonly=True) as session:
            response = await session.execute(query)
            results = response.scalars().all()
        return results
