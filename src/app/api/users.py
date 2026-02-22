import time

import fastapi
import pydantic

from app.domain.user_service import UserService, UserDto

router = fastapi.APIRouter()


class UserResponse(pydantic.BaseModel):
    elapsed: int
    size: int
    data: list[UserDto]


@router.get("")
async def get_users(
    size: int = fastapi.Query(100),
    user_service: UserService = fastapi.Depends(),
):
    start = time.perf_counter() * 1000
    data = await user_service.get_users(size)
    end = time.perf_counter() * 1000
    elapsed = int(end - start)
    return UserResponse(data=data, elapsed=elapsed, size=size)
