import fastapi

from app.notification.notification_service import NotificationService

router = fastapi.APIRouter()


# {"endpoint":"https://fcm.googleapis.com/fcm/send/cmvBgYwuP_c:APA91bFDR_xYcw-owzDqb17pTD3rb0n_0rTmjb9LN26qIJC1fB7LRaQhmP1vwRWwftrk7GFaLkM3ADgJVtWUWzIeNT4F3p1ZIJGyhGmtQqHvlr6imkQl2a4gFaILMYK0WFmMKXHGC9if","expirationTime":null,"keys":{"p256dh":"BAaTp-QmFbiWMeLBbIizWm8nLRZQ_ZD4LOxi3i63yCyOursBNMcVTczsePgRT7aGqf4CQ64lBl2KFYv9293Bp5w","auth":"K_8ACkP1UJgP96SjBLY3-g"}}
#
# class SubscribeRequestKeys(pydantic.BaseModel):
#     p256dh: str
#     auth: str
#
# class SubscribeRequest(pydantic.BaseModel):
#     endpoint: str
#     expirationTime: int | None = None
#     keys: SubscribeRequestKeys


@router.put("/subscribe", status_code=204)
async def subscribe(
    request: fastapi.Request,
    # payload: SubscribeRequest = fastapi.Body(...),
    notification_service: NotificationService = fastapi.Depends(),
):
    sub = await request.json()
    await notification_service.subscribe(sub)


@router.delete("/unsubscribe", status_code=204)
async def unsubscribe(
    request: fastapi.Request,
    notification_service: NotificationService = fastapi.Depends(),
):
    sub = await request.json()
    await notification_service.unsubscribe(sub)


@router.post("/say-hello", status_code=204)
async def say_hello(
    notification_service: NotificationService = fastapi.Depends(),
):
    await notification_service.say_hello()
