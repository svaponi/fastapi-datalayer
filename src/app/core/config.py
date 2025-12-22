import enum
import uuid

import pydantic
import pydantic_settings
from pydantic_settings import SettingsConfigDict

from app.core.cors import CorsConfig
from app.email.email_client_factory import EmailConfig


class EnvName(enum.StrEnum):
    production = "production"
    development = "development"
    local = "local"


class LogConfig(pydantic_settings.BaseSettings):
    LEVEL: str = "INFO"
    AS_JSON: bool = False
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
    )


class AppConfig(pydantic_settings.BaseSettings):
    APP_NAME: str = "foobar"
    ENV_NAME: EnvName = EnvName.local
    VERSION: str = "undefined"
    DOCS_ENABLED: bool = False
    TOKEN_SECRET: str = pydantic.Field(default_factory=lambda: uuid.uuid4().hex)
    cors: CorsConfig = pydantic.Field(default_factory=CorsConfig)
    log: LogConfig = pydantic.Field(default_factory=LogConfig)
    email: EmailConfig = pydantic.Field(default_factory=EmailConfig)

    def is_prod(self):
        return self.ENV_NAME == EnvName.production

    def get_app_name(self):
        name = self.APP_NAME.capitalize()
        return name if self.is_prod() else f"{name} {self.ENV_NAME.capitalize()}"
