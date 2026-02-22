import logging
import os
import time

from asyncpg_datalayer.db import DB

from app.datalayer.facade import DatalayerFacade
from app.datalayer.users import UsersRecordInsert

logger = logging.getLogger(__name__)


async def create_some_data(db: DB):
    facade = DatalayerFacade(db)

    num_of_users = os.getenv("APP_SEED_SIZE", default=None) or 10000

    emails = await facade.users.get_distinct_emails()
    insert_objs: list[UsersRecordInsert] = []
    for i in range(1, num_of_users + 1):
        email = f"user+{i}@example.com"
        if email not in emails:
            insert_objs.append(UsersRecordInsert(email=email))

    start = time.perf_counter()

    batch_size = 500
    for i in range(0, len(insert_objs), batch_size):
        batch = insert_objs[i : i + batch_size]
        await facade.users.insert_many(batch)

    end = time.perf_counter()
    elapsed = int((end - start) * 1000)
    logger.info(f"Create {num_of_users} users finished, elapsed {elapsed} ms")
