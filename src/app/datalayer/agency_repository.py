import sys
import uuid


import fastapi

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class AgencyTable(Base):
    __tablename__ = "agency"
    __table_args__ = (sqlalchemy.PrimaryKeyConstraint("agency_id", name="agency_pkey"),)
    agency_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    agency_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )
    agency_display_name: sqlalchemy.orm.Mapped[str | None] = (
        sqlalchemy.orm.mapped_column(sqlalchemy.String)
    )


AgencyRecord = AgencyTable


class AgencyRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    agency_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    agency_name: str
    agency_display_name: str | None = None


class AgencyRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    agency_name: str | None = None
    agency_display_name: str | None = None


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


class AgencyRepository(BaseRepository[AgencyRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, AgencyRecord)

    ### custom methods go below ###
