import fastapi
import pydantic_settings
from starlette.middleware.cors import CORSMiddleware


class CorsConfig(pydantic_settings.BaseSettings):
    CORS_ENABLED: bool = False
    CORS_ALLOW_ORIGINS: str | None = None
    CORS_ALLOW_ORIGIN_REGEX: str | None = None


def setup_cors(app: fastapi.FastAPI, cors: CorsConfig):
    if not cors.CORS_ENABLED:
        return
    allow_origins = cors.CORS_ALLOW_ORIGINS or ["*"]
    allow_origin_regex = cors.CORS_ALLOW_ORIGIN_REGEX
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
