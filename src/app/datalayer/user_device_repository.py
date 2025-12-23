import sys
import uuid

import fastapi
import pydantic
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB


class UserDeviceTable(Base):
    __tablename__ = "user_device"
    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint("user_device_id", name="user_device_pkey"),
    )
    user_device_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid,
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    auth_user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Uuid
    )
    subscription_info: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String
    )


UserDeviceRecord = UserDeviceTable


class UserDeviceRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    user_device_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    auth_user_id: uuid.UUID
    subscription_info: str | None = None


class UserDeviceRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    auth_user_id: uuid.UUID | None = None
    subscription_info: str | None = None


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


class UserDeviceRepository(BaseRepository[UserDeviceRecord]):
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__(db, UserDeviceRecord)

    ### custom methods go below ###
