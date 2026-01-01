import asyncio
import datetime
import logging
import uuid

import fastapi
import pydantic

from app.api.dependencies import get_auth
from app.auth.auth_service import AuthDto
from app.datalayer.chat import ChatRecordInsert
from app.datalayer.facade import DatalayerFacade


class Chat(pydantic.BaseModel):
    chat_id: uuid.UUID
    chat_title: str
    user_ids: list[uuid.UUID]
    latest_message: datetime.datetime | None = None
    message_count: int | None = None
    unread_message_count: int | None = None


class ChatService:

    def __init__(
        self,
        auth: AuthDto = fastapi.Depends(get_auth),
        facade: DatalayerFacade = fastapi.Depends(),
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.user_id = auth.user.user_id
        self.facade = facade

    async def create_chat(
        self,
        user_ids: list[uuid.UUID] | None = None,
    ) -> uuid.UUID:
        if not user_ids:
            user_ids = [au.user_id for au in await self.facade.user_account.get_all()]
        chat_id = await self.facade.chat.insert(ChatRecordInsert(user_ids=user_ids))
        return chat_id

    async def get_chats(self) -> list[Chat]:
        chats = await self.facade.chat.get_all()
        return await self.enhance_all(chats)

    async def get_chat(self, chat_id: uuid.UUID) -> Chat | None:
        c = await self.facade.chat.get_or_none_by_id(chat_id)
        if not c:
            return None
        return await self.enhance_one(c)

    async def enhance_one(self, record: Chat) -> Chat:
        return (await self.enhance_all([record]))[0]

    async def enhance_all(self, records: list[Chat]) -> list[Chat]:
        chat_ids = {c.chat_id for c in records}
        aggregated_by_chat_id, unread_by_chat_id = await asyncio.gather(
            self.facade.chat_message.aggregate_chats(chat_ids=chat_ids),
            self.facade.chat_message.count_unread(
                chat_ids=chat_ids,
                user_id=self.user_id,
            ),
        )

        def gen():
            for c in records:
                unread_message_count = unread_by_chat_id.get(c.chat_id)
                aggregated = aggregated_by_chat_id.get(c.chat_id)
                message_count = None
                latest_message = None
                if aggregated:
                    message_count, latest_message = aggregated
                yield Chat(
                    chat_id=c.chat_id,
                    chat_title=c.chat_title or c.chat_id.hex[:8],
                    user_ids=c.user_ids,
                    latest_message=latest_message,
                    message_count=message_count,
                    unread_message_count=unread_message_count,
                )

        return list(gen())
