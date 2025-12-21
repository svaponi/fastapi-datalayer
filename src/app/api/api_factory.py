import fastapi

from app.api import auth, health


def setup_api(app: fastapi.FastAPI):
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(health.router, prefix="/api/health", tags=["health"])
