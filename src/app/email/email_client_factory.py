import pydantic_settings

from app.email.clients.dummy_client import DummyEmailClient
from app.email.clients.gmail_client import GmailEmailClient
from app.email.email_client import EmailClient


class EmailConfig(pydantic_settings.BaseSettings):
    GMAIL_USERNAME: str | None = None
    GMAIL_PASSWORD: str | None = None
    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="EMAIL_",
    )


def create_email_client(config: EmailConfig) -> EmailClient:
    if config.GMAIL_PASSWORD and config.GMAIL_USERNAME:
        return GmailEmailClient(
            username=config.GMAIL_USERNAME,
            app_password=config.GMAIL_PASSWORD,
        )
    else:
        return DummyEmailClient()
