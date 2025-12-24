import logging

from asyncpg_datalayer.db import DB

from app.auth.utils import hash_password
from app.datalayer.auth_user_repository import AuthUserRepository, AuthUserRecordInsert

logger = logging.getLogger(__name__)


async def create_defaults(db: DB):
    auth_user_repo = AuthUserRepository(db)
    jdoe = await auth_user_repo.find_by_email("jdoe@example.com")
    if not jdoe:
        await auth_user_repo.insert(
            AuthUserRecordInsert(
                email="jdoe@example.com",
                hashed_password=hash_password("secret"),
                full_name="Jane Doe",
            )
        )
