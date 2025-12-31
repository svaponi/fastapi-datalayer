import asyncio
import datetime
import logging
import uuid

import fastapi
import pydantic

from app.api.dependencies import get_auth
from app.auth.auth_service import AuthDto
from app.core.config import AppConfig, NotificationConfig
from app.core.dependencies import get_app_config
from app.datalayer.chat import ChatRecordInsert, ChatRecord
from app.datalayer.chat_message import ChatMessageRecordInsert
from app.datalayer.chat_message_to_user import (
    ChatMessageToUserRecordInsert,
    ChatMessageToUserRecordUpdate,
)
from app.datalayer.facade import DatalayerFacade
from app.notification.notification_service import NotificationService


def get_notification_config(
    config: AppConfig = fastapi.Depends(get_app_config),
) -> NotificationConfig:
    return config.notification


def get_sub_id(subscription_info: dict) -> uuid.UUID:
    endpoint = subscription_info.get("endpoint")
    if not endpoint:
        raise ValueError("Invalid subscription_info: missing endpoint")
    return uuid.uuid5(uuid.NAMESPACE_DNS, endpoint)


class ChatMessage(pydantic.BaseModel):
    chat_id: uuid.UUID
    chat_message_id: uuid.UUID
    from_user_id: uuid.UUID
    entered_at: datetime.datetime
    read_at: datetime.datetime | None
    content: str


class MessageService:

    def __init__(
        self,
        auth: AuthDto = fastapi.Depends(get_auth),
        facade: DatalayerFacade = fastapi.Depends(),
        notification_service: NotificationService = fastapi.Depends(),
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.auth = auth
        self.facade = facade
        self.notification_service = notification_service

    async def create_chat(
        self,
        user_ids: list[uuid.UUID] | None = None,
    ) -> uuid.UUID:
        if not user_ids:
            user_ids = [
                au.auth_user_id for au in await self.facade.user_account.get_all()
            ]
        chat_id = await self.facade.chat.insert(ChatRecordInsert(user_ids=user_ids))
        return chat_id

    async def create_message(
        self,
        chat_id: uuid.UUID,
        content: str,
        notify_users: bool = False,
    ):
        chat = await self.facade.chat.get_or_none_by_id(chat_id)
        if not chat:
            raise ValueError("chat not found")
        to_user_ids = set(chat.auth_user_ids) - {self.auth.user_id}
        async with self.facade.chat_message_to_user.get_session() as session:
            chat_message_id = await self.facade.chat_message.insert(
                ChatMessageRecordInsert(
                    chat_id=chat_id,
                    from_user_id=self.auth.user_id,
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
                "chat_id": chat_id,
                "chat_message_id": chat_message_id,
                "to_user_id": self.auth.user_id,
            },
        )
        return rowcount

    async def get_chats(self) -> list[ChatRecord]:
        chats = await self.facade.chat.get_all()
        return chats

    async def get_received_chat_messages(self, chat_id: uuid.UUID) -> list[ChatMessage]:
        chat_message_to_users = await self.facade.chat_message_to_user.get_all(
            filters={"chat_id": chat_id, "to_user_id": self.auth.user_id}
        )
        by_chat_message_id = {cmr.chat_message_id: cmr for cmr in chat_message_to_users}
        chat_message_ids = set(cmr.chat_message_id for cmr in chat_message_to_users)
        received_chat_messages = await self.facade.chat_message_to_user.get_by_ids(
            chat_message_ids
        )
        return [
            ChatMessage(
                chat_id=m.chat_id,
                chat_message_id=m.chat_message_id,
                from_user_id=m.from_user_id,
                entered_at=m.entered_at,
                read_at=by_chat_message_id.get(m.chat_message_id).read_at,
                content=m.content or "",
            )
            for m in received_chat_messages.values()
        ]

    async def get_sent_chat_messages(self, chat_id: uuid.UUID) -> list[ChatMessage]:
        messages = await self.facade.chat_message.get_all(
            filters={"chat_id": chat_id, "from_user_id": self.auth.user_id}
        )
        return [
            ChatMessage(
                chat_id=m.chat_id,
                chat_message_id=m.chat_message_id,
                from_user_id=m.from_user_id,
                entered_at=m.entered_at,
                read_at=None,
                content=m.content or "",
            )
            for m in messages
        ]

    async def get_chat_messages(self, chat_id: uuid.UUID) -> list[ChatMessage]:
        received, sent = await asyncio.gather(
            self.get_received_chat_messages(chat_id),
            self.get_sent_chat_messages(chat_id),
        )
        return received + sent
