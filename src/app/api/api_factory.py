import fastapi

from app.api import auth, health, notifications, chats


def setup_api(app: fastapi.FastAPI):
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(health.router, prefix="/api/health", tags=["health"])
    app.include_router(
        notifications.router, prefix="/api/notifications", tags=["notifications"]
    )
    app.include_router(chats.router, prefix="/api/chats", tags=["chats"])
