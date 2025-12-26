import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm

from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class _AgencyTable(Base):
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


AgencyRecord = _AgencyTable


class AgencyRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    agency_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    agency_name: str
    agency_display_name: str | None = None


class AgencyRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    agency_name: str | None = None
    agency_display_name: str | None = None


class AgencyRepository(BaseRepository[AgencyRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, AgencyRecord)

    ### custom methods go below ###
