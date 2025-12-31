import datetime
import uuid

import fastapi
import pydantic

from app.auth.user_service import UserService
from app.domain.messages.message_service import MessageService

router = fastapi.APIRouter()


class ChatDto(pydantic.BaseModel):
    chat_id: uuid.UUID
    user_ids: list[uuid.UUID]


@router.get("")
async def get_chats(
    message_service: MessageService = fastapi.Depends(),
) -> list[ChatDto]:
    messages = await message_service.get_chats()
    return [
        ChatDto(
            chat_id=msg.chat_id,
            user_ids=msg.auth_user_ids,
        )
        for msg in messages
    ]


@router.post("")
async def new_chat(
    message_service: MessageService = fastapi.Depends(),
) -> uuid.UUID:
    return await message_service.create_chat()


class ChatMessageCreateRequest(pydantic.BaseModel):
    content: str


@router.post("/{chat_id}/messages")
async def new_message(
    chat_id: uuid.UUID,
    payload: ChatMessageCreateRequest = fastapi.Body(...),
    message_service: MessageService = fastapi.Depends(),
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


@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: uuid.UUID,
    message_service: MessageService = fastapi.Depends(),
    user_service: UserService = fastapi.Depends(),
) -> list[ChatMessageDto]:
    messages = await message_service.get_chat_messages(chat_id)
    user_ids = {msg.from_user_id for msg in messages}
    email_by_ids = await user_service.get_email_by_ids(user_ids)
    return [
        ChatMessageDto(
            chat_id=msg.chat_id,
            chat_message_id=msg.chat_message_id,
            from_user_id=msg.from_user_id,
            from_user_display_name=email_by_ids.get(msg.from_user_id, "unknown"),
            entered_at=msg.entered_at,
            read_at=msg.read_at,
            content=msg.content,
        )
        for msg in messages
    ]


@router.put("/{chat_id}/messages/{chat_message_id}/read", status_code=204)
async def set_message_read(
    chat_id: uuid.UUID,
    chat_message_id: uuid.UUID,
    message_service: MessageService = fastapi.Depends(),
):
    await message_service.set_message_read(chat_id, chat_message_id)
