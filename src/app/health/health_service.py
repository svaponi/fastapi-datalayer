import logging

import fastapi
import sqlalchemy
from asyncpg_datalayer.db import DB


def get_db(request: fastapi.Request) -> DB:
    if not hasattr(request.app.state, "db"):
        raise RuntimeError("DB not found in app.state")
    return request.app.state.db


class HealthService:
    def __init__(
        self,
        db: DB = fastapi.Depends(get_db),
    ) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{self.__module__}.{type(self).__name__}")
        self.db = db

    async def check(self) -> bool:
        status = await self._check_db()
        return status

    async def _check_db(self) -> bool:
        try:
            async with self.db.get_session(readonly=True) as session:
                response = await session.execute(sqlalchemy.text("SELECT 1"))
                result = response.scalar_one_or_none()
            return result == 1
        except Exception as e:
            self.logger.error(e)
            return False
