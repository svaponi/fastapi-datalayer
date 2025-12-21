import fastapi
from starlette.responses import JSONResponse

from app.health.health_service import HealthService

router = fastapi.APIRouter()


@router.get("")
async def health(
    health_service: HealthService = fastapi.Depends(),
):
    ok = await health_service.check()
    if ok:
        return JSONResponse({"status": "up"}, status_code=200)
    else:
        return JSONResponse({"status": "down"}, status_code=503)
