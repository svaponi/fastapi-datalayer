import pydantic
import pydantic_settings

from app.core.logs import LogConfig


class AppConfig(pydantic_settings.BaseSettings):
    APP_NAME: str = "foobar"
    VERSION: str = "undefined"
    DOCS_ENABLED: bool = False
    log: LogConfig = pydantic.Field(default_factory=LogConfig)

    def get_app_name(self):
        return self.APP_NAME.capitalize()
