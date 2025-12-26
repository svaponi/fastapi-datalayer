import asyncio
import logging

from asyncpg_datalayer.db import DB

from app.auth.utils import hash_password
from app.datalayer.auth_user import AuthUserRepository, AuthUserRecordInsert

logger = logging.getLogger(__name__)


async def create_defaults(db: DB):
    auth_user_repo = AuthUserRepository(db)

    # TODO change with select distinct emails
    users = await auth_user_repo.get_all()
    user_by_email = {user.email: user for user in users}

    async def create_user_if_missing(email: str, full_name: str | None = None):
        user = user_by_email.get(email)
        if not user:
            await auth_user_repo.insert(
                AuthUserRecordInsert(
                    email=email,
                    hashed_password=hash_password("secret"),
                    full_name=full_name,
                )
            )

    await asyncio.gather(
        create_user_if_missing("jdoe@example.com", full_name="Jane Doe"),
        create_user_if_missing("sam@example.com"),
        create_user_if_missing("alice@example.com"),
        create_user_if_missing("bob@example.com"),
    )
