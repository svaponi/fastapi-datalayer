import json
import logging
import uuid

import fastapi
import pywebpush
from asyncpg_datalayer.errors import ConstraintViolationException

from app.api.dependencies import get_auth_user
from app.auth.auth_service import AuthUserDto
from app.core.config import AppConfig, NotificationConfig
from app.core.dependencies import get_app_config
from app.datalayer.user_device_repository import (
    UserDeviceRepository,
    UserDeviceRecordInsert,
)


def get_notification_config(
    config: AppConfig = fastapi.Depends(get_app_config),
) -> NotificationConfig:
    return config.notification


def get_sub_id(subscription_info: dict) -> uuid.UUID:
    endpoint = subscription_info.get("endpoint")
    if not endpoint:
        raise ValueError("Invalid subscription_info: missing endpoint")
    return uuid.uuid5(uuid.NAMESPACE_DNS, endpoint)


class NotificationService:

    def __init__(
        self,
        auth_user: AuthUserDto = fastapi.Depends(get_auth_user),
        user_device_repo: UserDeviceRepository = fastapi.Depends(),
        notification_config: NotificationConfig = fastapi.Depends(
            get_notification_config
        ),
    ) -> None:
        self.auth_user = auth_user
        self.user_device_repo = user_device_repo
        self.vapid_private_key = notification_config.VAPID_PRIVATE_KEY
        self.logger = logging.getLogger(__name__)

    async def unsubscribe(self, subscription_info: dict):
        sub_id = get_sub_id(subscription_info)
        rowcount = await self.user_device_repo.delete_by_id(sub_id)
        if rowcount:
            self.logger.info(f"Removed subscription {subscription_info}")
        else:
            self.logger.info(f"Subscription not found {subscription_info}")
        return None

    async def subscribe(self, subscription_info: dict) -> uuid.UUID:
        sub_id = get_sub_id(subscription_info)
        try:
            await self.user_device_repo.insert(
                UserDeviceRecordInsert(
                    user_device_id=sub_id,
                    auth_user_id=self.auth_user.user_id,
                    subscription_info=json.dumps(subscription_info),
                )
            )
            self.logger.info(f"Saved subscription {subscription_info}")
        except ConstraintViolationException:
            self.logger.info(f"Subscription already exists {subscription_info}")
        return sub_id

    async def say_hello(self):
        if not self.vapid_private_key:
            raise RuntimeError(
                "VAPID keys not configured, cannot send push notifications"
            )

        payload = {
            "title": "Hello!",
            "body": f"Greeting from {self.auth_user.email}",
            "url": "/",
        }

        data = json.dumps(payload)
        subscriptions = await self.user_device_repo.get_all()
        for sub in subscriptions:
            if not sub.subscription_info:
                continue
            subscription_info = json.loads(sub.subscription_info)
            try:
                self.logger.info(f"Sending push to {subscription_info}")
                pywebpush.webpush(
                    subscription_info=subscription_info,
                    data=data,
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims={"sub": "mailto:you@example.com"},
                )
            except pywebpush.WebPushException as e:
                self.logger.error(e.message)
                if e.response.status_code == 410:
                    await self.unsubscribe(subscription_info)
