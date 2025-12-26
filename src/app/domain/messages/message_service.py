import logging
import uuid

import fastapi

from app.api.dependencies import get_auth_user
from app.auth.auth_service import AuthUserDto
from app.core.config import AppConfig, NotificationConfig
from app.core.dependencies import get_app_config
from app.datalayer.auth_user_repository import AuthUserRepository
from app.datalayer.chat_message_recipient_repository import (
    ChatMessageRecipientRecordInsert,
    ChatMessageRecipientRepository,
)
from app.datalayer.chat_message_repository import (
    ChatMessageRepository,
    ChatMessageRecordInsert,
    ChatMessageRecord,
)
from app.datalayer.chat_repository import ChatRepository, ChatRecordInsert, ChatRecord
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


class MessageService:

    def __init__(
        self,
        auth_user: AuthUserDto = fastapi.Depends(get_auth_user),
        auth_user_repo: AuthUserRepository = fastapi.Depends(),
        chat_repo: ChatRepository = fastapi.Depends(),
        chat_message_repo: ChatMessageRepository = fastapi.Depends(),
        chat_message_recipient_repo: ChatMessageRecipientRepository = fastapi.Depends(),
        notification_service: NotificationService = fastapi.Depends(),
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.auth_user = auth_user
        self.auth_user_repo = auth_user_repo
        self.chat_repo = chat_repo
        self.chat_message_repo = chat_message_repo
        self.chat_message_recipient_repo = chat_message_recipient_repo
        self.notification_service = notification_service

    async def create_chat(
        self,
        auth_user_ids: list[uuid.UUID] | None = None,
    ) -> uuid.UUID:
        if not auth_user_ids:
            auth_user_ids = [
                au.auth_user_id for au in await self.auth_user_repo.get_all()
            ]
        chat_id = await self.chat_repo.insert(
            ChatRecordInsert(auth_user_ids=auth_user_ids)
        )
        return chat_id

    async def create_message(
        self,
        chat_id: uuid.UUID,
        content: str,
    ):
        chat = await self.chat_repo.get_or_none_by_id(chat_id)
        if not chat:
            raise ValueError("chat not found")
        async with self.chat_message_repo.get_session() as session:
            chat_message_id = await self.chat_message_repo.insert(
                ChatMessageRecordInsert(
                    chat_id=chat_id,
                    from_user_id=self.auth_user.user_id,
                    content=content,
                ),
                reuse_session=session,
            )
            for to_user_id in chat.auth_user_ids:
                await self.chat_message_recipient_repo.insert(
                    ChatMessageRecipientRecordInsert(
                        chat_id=chat_id,
                        chat_message_id=chat_message_id,
                        to_user_id=to_user_id,
                    ),
                    reuse_session=session,
                )
        payload = {
            "title": "New message",
            "url": f"/chat/{chat_id}?chat_message_id={chat_message_id}",
        }
        await self.notification_service.send(payload)
        return chat_message_id

    async def get_chats(self) -> list[ChatRecord]:
        chats = await self.chat_repo.get_all()
        return chats

    async def get_chat_messages(self, chat_id: uuid.UUID) -> list[ChatMessageRecord]:
        chat_message_recs = await self.chat_message_recipient_repo.get_all(
            filters={"chat_id": chat_id, "to_user_id": self.auth_user.user_id}
        )
        chat_message_ids = set(cmr.chat_message_id for cmr in chat_message_recs)
        chat_messages = await self.chat_message_repo.get_by_ids(chat_message_ids)
        return list(chat_messages.values())
