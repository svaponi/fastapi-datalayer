import asyncio
import logging

from asyncpg_datalayer.db import DB

from app.auth.user_service import UserService
from app.datalayer.facade import DatalayerFacade

logger = logging.getLogger(__name__)


async def create_defaults(db: DB):
    facade = DatalayerFacade(db)
    user_service = UserService(facade)

    # TODO change with select distinct emails
    emails = await user_service.get_distinct_emails()

    async def create_user_if_missing(email: str, full_name: str | None = None):
        if email not in emails:
            await user_service.create_user(
                email=email,
                password="secret",
                full_name=full_name,
            )

    await asyncio.gather(
        create_user_if_missing("jdoe@example.com", full_name="Jane Doe"),
        create_user_if_missing("sam@example.com"),
        create_user_if_missing("alice@example.com"),
        create_user_if_missing("bob@example.com"),
    )
