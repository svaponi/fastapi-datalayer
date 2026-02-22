import fastapi

from app.api import health, users


def setup_api(app: fastapi.FastAPI):
    app.include_router(health.router, prefix="/api/health", tags=["health"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
