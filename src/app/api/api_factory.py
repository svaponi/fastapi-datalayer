import fastapi

from app.api import auth


def setup_api(app: fastapi.FastAPI):
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
