import datetime
import uuid

import pydantic
import sqlalchemy
import sqlalchemy.orm
from asyncpg_datalayer.base_repository import BaseRepository
from asyncpg_datalayer.base_table import Base
from asyncpg_datalayer.db import DB
from asyncpg_datalayer.types import Filters

from app.datalayer.chat_message_to_user import _ChatMessageToUserTable


class _ChatMessageTable(Base):
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


ChatMessageRecord = _ChatMessageTable


class ChatMessageRecordInsert(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    chat_id: uuid.UUID
    from_user_id: uuid.UUID
    entered_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now
    )
    content: str | None = None


class ChatMessageRecordUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chat_id: uuid.UUID | None = None
    from_user_id: uuid.UUID | None = None
    entered_at: datetime.datetime | None = None
    content: str | None = None


class ChatMessageRepository(BaseRepository[ChatMessageRecord]):
    def __init__(self, db: DB) -> None:
        super().__init__(db, ChatMessageRecord)

    ### custom methods go below ###

    async def aggregate_chats(
        self,
        chat_ids: list[uuid.UUID] | None = None,
        filters: Filters | None = None,
    ) -> dict[uuid.UUID, tuple[int, datetime.datetime]]:
        query = sqlalchemy.select(
            _ChatMessageTable.chat_id,
            sqlalchemy.func.count(1),
            sqlalchemy.func.max(_ChatMessageTable.entered_at),
        ).group_by(_ChatMessageTable.chat_id)

        if chat_ids is not None:
            query = query.where(_ChatMessageTable.chat_id.in_(chat_ids))

        if filters:
            query = self._with_filters(query, filters)

        async with self.db.get_session(readonly=True) as session:
            response = await session.execute(query)
            list_of_tuples: list[tuple] = response.all()
            results = {t[0]: (t[1], t[2]) for t in list_of_tuples}
        return results

    async def count_unread(
        self,
        user_id: uuid.UUID,
        chat_ids: list[uuid.UUID] | None = None,
        filters: Filters | None = None,
    ) -> dict[uuid.UUID, int]:
        query = (
            sqlalchemy.select(
                _ChatMessageTable.chat_id,
                sqlalchemy.func.count(
                    sqlalchemy.distinct(_ChatMessageTable.chat_message_id)
                ),
            )
            .join(
                _ChatMessageToUserTable,
                _ChatMessageTable.chat_message_id
                == _ChatMessageToUserTable.chat_message_id,
            )
            .where(
                _ChatMessageToUserTable.to_user_id == user_id,
                _ChatMessageToUserTable.read_at.is_(None),
            )
            .group_by(_ChatMessageTable.chat_id)
        )

        if chat_ids is not None:
            query = query.where(_ChatMessageTable.chat_id.in_(chat_ids))

        if filters:
            query = self._with_filters(query, filters)

        async with self.db.get_session(readonly=True) as session:
            response = await session.execute(query)
            list_of_tuples: list[tuple] = response.all()
            results = {t[0]: t[1] for t in list_of_tuples}
        return results
