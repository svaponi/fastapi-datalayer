import datetime

import pytest

from app.datalayer.chat import ChatRecordInsert
from app.datalayer.chat_message import ChatMessageRecordInsert
from app.datalayer.user_account import UserAccountRecordInsert


@pytest.mark.asyncio
async def test_scrolling_order(facade):
    from_user_id = await facade.user_account.insert(
        UserAccountRecordInsert(email="test@example.com")
    )
    chat_id = await facade.chat.insert(ChatRecordInsert())
    repo = facade.chat_message
    entered_at = datetime.datetime.now()
    inserted_ids = [
        await repo.insert(
            ChatMessageRecordInsert(
                chat_id=chat_id,
                from_user_id=from_user_id,
                entered_at=entered_at + datetime.timedelta(minutes=i),
                content=f"Message {i}",
            )
        )
        for i in range(10)
    ]

    page_1, count_1, cursor_1 = await repo.scroll(
        size=8,
        sort_by="entered_at",
    )
    assert len(page_1) == 8
    assert count_1 == 10
    assert page_1[0].chat_message_id == inserted_ids[0]
    assert page_1[7].chat_message_id == inserted_ids[7]
    page_2, count_2, cursor_2 = await repo.scroll(
        cursor=cursor_1,
        size=8,
        sort_by="entered_at",
        skip_count=True,
    )
    assert len(page_2) == 2
    assert count_2 == -1
    assert page_2[0].chat_message_id == inserted_ids[8]
    assert page_2[1].chat_message_id == inserted_ids[9]

    page_1, count_1, cursor_1 = await repo.scroll(
        size=8,
        sort_by="entered_at:desc",
    )
    assert len(page_1) == 8
    assert count_1 == 10
    assert page_1[0].chat_message_id == inserted_ids[9]
    assert page_1[7].chat_message_id == inserted_ids[2]
    page_2, count_2, cursor_2 = await repo.scroll(
        cursor=cursor_1,
        size=8,
        sort_by="entered_at:desc",
        skip_count=True,
    )
    assert len(page_2) == 2
    assert count_2 == -1
    assert page_2[0].chat_message_id == inserted_ids[1]
    assert page_2[1].chat_message_id == inserted_ids[0]
