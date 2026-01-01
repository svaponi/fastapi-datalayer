import datetime
import uuid

import fastapi
import pydantic

from app.auth.user_service import UserService
from app.core.errors import NotFoundException
from app.domain.chat.chat_message_service import ChatMessageService
from app.domain.chat.chat_service import ChatService

router = fastapi.APIRouter()


class ChatDto(pydantic.BaseModel):
    chat_id: uuid.UUID
    chat_title: str
    latest_message: datetime.datetime | None
    message_count: int
    has_unread: bool


@router.get("")
async def get_chats(
    chat_service: ChatService = fastapi.Depends(),
) -> list[ChatDto]:
    chats = await chat_service.get_chats()
    return [
        ChatDto(
            chat_id=chat.chat_id,
            chat_title=chat.chat_title,
            latest_message=chat.latest_message,
            message_count=chat.message_count or 0,
            has_unread=chat.unread_message_count and chat.unread_message_count > 0,
        )
        for chat in chats
    ]


@router.post("")
async def create_chat(
    chat_service: ChatService = fastapi.Depends(),
) -> uuid.UUID:
    return await chat_service.create_chat()


@router.get("/{chat_id}")
async def get_chat(
    chat_id: uuid.UUID,
    chat_service: ChatService = fastapi.Depends(),
) -> ChatDto:
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise NotFoundException()
    return ChatDto(
        chat_id=chat.chat_id,
        chat_title=chat.chat_title,
        latest_message=chat.latest_message,
        message_count=chat.message_count or 0,
        has_unread=chat.unread_message_count and chat.unread_message_count > 0,
    )


class ChatMessageCreateRequest(pydantic.BaseModel):
    content: str


@router.post("/{chat_id}/messages")
async def create_message(
    chat_id: uuid.UUID,
    payload: ChatMessageCreateRequest = fastapi.Body(...),
    message_service: ChatMessageService = fastapi.Depends(),
) -> uuid.UUID:
    return await message_service.create_message(chat_id, payload.content)


class ChatMessageDto(pydantic.BaseModel):
    chat_id: uuid.UUID
    chat_message_id: uuid.UUID
    from_user_id: uuid.UUID
    from_user_display_name: str
    entered_at: datetime.datetime
    read_at: datetime.datetime | None
    content: str


class ChatMessagesDto(pydantic.BaseModel):
    data: list[ChatMessageDto]
    cursor: str | None = None


@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: uuid.UUID,
    message_service: ChatMessageService = fastapi.Depends(),
    user_service: UserService = fastapi.Depends(),
    size: int | None = fastapi.Query(None),
    cursor: str | None = fastapi.Query(None),
) -> ChatMessagesDto:
    messages, cursor = await message_service.get_latest_chat_messages(
        chat_id, size=size, cursor=cursor
    )
    user_ids = {msg.from_user_id for msg in messages}
    display_name_by_ids = await user_service.get_display_name_by_ids(user_ids)
    return ChatMessagesDto(
        data=[
            ChatMessageDto(
                chat_id=msg.chat_id,
                chat_message_id=msg.chat_message_id,
                from_user_id=msg.from_user_id,
                from_user_display_name=display_name_by_ids.get(
                    msg.from_user_id, "unknown"
                ),
                entered_at=msg.entered_at,
                read_at=msg.read_at,
                content=msg.content,
            )
            for msg in messages
        ],
        cursor=cursor,
    )


@router.get("/{chat_id}/messages/{chat_message_id}")
async def get_message(
    chat_id: uuid.UUID,
    chat_message_id: uuid.UUID,
    message_service: ChatMessageService = fastapi.Depends(),
    user_service: UserService = fastapi.Depends(),
) -> ChatMessageDto:
    msg = await message_service.get_chat_message(chat_id, chat_message_id)
    if not msg:
        raise NotFoundException()
    display_name_by_ids = await user_service.get_display_name_by_ids({msg.from_user_id})
    return ChatMessageDto(
        chat_id=msg.chat_id,
        chat_message_id=msg.chat_message_id,
        from_user_id=msg.from_user_id,
        from_user_display_name=display_name_by_ids.get(msg.from_user_id, "unknown"),
        entered_at=msg.entered_at,
        read_at=msg.read_at,
        content=msg.content,
    )


@router.put("/{chat_id}/messages/{chat_message_id}/read", status_code=204)
async def mark_message_as_read(
    chat_id: uuid.UUID,
    chat_message_id: uuid.UUID,
    message_service: ChatMessageService = fastapi.Depends(),
):
    await message_service.set_message_read(chat_id, chat_message_id)
