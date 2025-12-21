import fastapi
import pydantic_settings
from starlette.middleware.cors import CORSMiddleware


class CorsConfig(pydantic_settings.BaseSettings):
    ENABLED: bool = False
    ALLOW_ORIGINS: str | None = None
    ALLOW_ORIGIN_REGEX: str | None = None
    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="CORS_",
    )


def setup_cors(app: fastapi.FastAPI, cors: CorsConfig):
    if not cors.ENABLED:
        return
    allow_origins = cors.ALLOW_ORIGINS or ["*"]
    allow_origin_regex = cors.ALLOW_ORIGIN_REGEX
    if isinstance(allow_origins, str):
        allow_origins = allow_origins.split(",")
    if allow_origin_regex:
        allow_origins = []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
