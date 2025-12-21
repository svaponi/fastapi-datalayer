import fastapi

from app.core.config import AppConfig


def get_app_config(req: fastapi.Request) -> AppConfig:
    return req.app.config


def get_login_link_ttl(config: AppConfig = fastapi.Depends(get_app_config)) -> int:
    return config.LOGIN_LINK_TTL
