import logging
import uuid
from typing import Iterable
from uuid import UUID

import fastapi

from app.api.dependencies import get_auth_user
from app.auth.auth_service import AuthUserDto
from app.datalayer.auth_user_repository import AuthUserRepository


class UserService:

    def __init__(
        self,
        auth_user: AuthUserDto = fastapi.Depends(get_auth_user),
        auth_user_repo: AuthUserRepository = fastapi.Depends(),
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.auth_user = auth_user
        self.auth_user_repo = auth_user_repo

    async def get_email_by_ids(
        self,
        auth_user_ids: Iterable[uuid.UUID],
    ) -> dict[UUID, str]:
        by_id = await self.auth_user_repo.get_by_ids(set(auth_user_ids))
        return {e.auth_user_id: e.email for e in by_id.values()}
