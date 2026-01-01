import datetime
import logging
import uuid

import fastapi
import pydantic

from app.api.dependencies import get_auth
from app.auth.auth_service import Auth
from app.datalayer.chat_message import ChatMessageRecordInsert, ChatMessageRecord
from app.datalayer.chat_message_to_user import (
    ChatMessageToUserRecordInsert,
    ChatMessageToUserRecordUpdate,
)
from app.datalayer.facade import DatalayerFacade
from app.notification.notification_service import NotificationService


class ChatMessage(pydantic.BaseModel):
    chat_id: uuid.UUID
    chat_message_id: uuid.UUID
    from_user_id: uuid.UUID
    entered_at: datetime.datetime
    read_at: datetime.datetime | None
    content: str


class ChatMessageService:

    def __init__(
        self,
        auth: Auth = fastapi.Depends(get_auth),
        facade: DatalayerFacade = fastapi.Depends(),
        notification_service: NotificationService = fastapi.Depends(),
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.user_id = auth.user.user_id
        self.facade = facade
        self.notification_service = notification_service

    async def create_message(
        self,
        chat_id: uuid.UUID,
        content: str,
        notify_users: bool = False,
    ):
        chat = await self.facade.chat.get_or_none_by_id(chat_id)
        if not chat:
            raise ValueError("chat not found")
        to_user_ids = set(chat.user_ids) - {self.user_id}
        async with self.facade.chat_message_to_user.get_session() as session:
            chat_message_id = await self.facade.chat_message.insert(
                ChatMessageRecordInsert(
                    chat_id=chat_id,
                    from_user_id=self.user_id,
                    content=content,
                ),
                reuse_session=session,
            )
            insert_objs = [
                ChatMessageToUserRecordInsert(
                    chat_message_id=chat_message_id,
                    to_user_id=to_user_id,
                )
                for to_user_id in to_user_ids
            ]
            await self.facade.chat_message_to_user.insert_many(
                insert_objs,
                reuse_session=session,
            )
        if notify_users:
            payload = {
                "title": "New message",
                "url": f"/chat/{chat_id}?chat_message_id={chat_message_id}",
            }
            await self.notification_service.send(payload, to_user_ids=to_user_ids)
        return chat_message_id

    async def set_message_read(
        self,
        chat_id: uuid.UUID,
        chat_message_id: uuid.UUID,
    ) -> int:
        read_at = datetime.datetime.now()
        rowcount = await self.facade.chat_message_to_user.update_many(
            ChatMessageToUserRecordUpdate(
                read_at=read_at,
            ),
            filters={
                "chat_message_id": chat_message_id,
                "to_user_id": self.user_id,
            },
        )
        return rowcount

    async def get_chat_message(
        self, chat_id: uuid.UUID, chat_message_id: uuid.UUID
    ) -> ChatMessage | None:
        record = await self.facade.chat_message.get_or_none_by_id(chat_message_id)

        if not record:
            return None
        return await self.enhance_one(record)

    async def get_latest_chat_messages(
        self,
        chat_id: uuid.UUID,
        size: int | None = None,
        cursor: str | None = None,
    ) -> tuple[list[ChatMessage], str]:
        records, _, cursor = await self.facade.chat_message.scroll(
            sort_by="entered_at:desc",
            size=size or 10,
            cursor=cursor,
            skip_count=True,
            filters={"chat_id": chat_id},
        )
        messages = await self.enhance_all(records)
        latest = sorted(messages, key=lambda m: m.entered_at, reverse=True)
        return latest, cursor

    async def enhance_one(self, record: ChatMessageRecord) -> ChatMessage:
        return (await self.enhance_all([record]))[0]

    async def enhance_all(self, records: list[ChatMessageRecord]) -> list[ChatMessage]:
        sent_messages = [m for m in records if m.from_user_id == self.user_id]
        received_messages = [m for m in records if m.from_user_id != self.user_id]
        received_message_ids = {m.chat_message_id for m in received_messages}
        received_message_by_id = {m.chat_message_id: m for m in received_messages}
        chat_message_to_users = await self.facade.chat_message_to_user.get_all(
            filters={
                "chat_message_id": received_message_ids,
                "to_user_id": self.user_id,
            }
        )

        def get_received():
            for m in chat_message_to_users:
                msg = received_message_by_id.get(m.chat_message_id)
                if not msg:
                    continue
                yield ChatMessage(
                    chat_id=msg.chat_id,
                    chat_message_id=msg.chat_message_id,
                    from_user_id=msg.from_user_id,
                    entered_at=msg.entered_at,
                    read_at=m.read_at,
                    content=msg.content,
                )

        def get_sent():
            for m in sent_messages:
                yield ChatMessage(
                    chat_id=m.chat_id,
                    chat_message_id=m.chat_message_id,
                    from_user_id=m.from_user_id,
                    entered_at=m.entered_at,
                    read_at=None,
                    content=m.content or "",
                )

        received = list(get_received())
        sent = list(get_sent())
        return received + sent
