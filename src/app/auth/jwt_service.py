import datetime
import typing

import fastapi.params
import jwt

from app.core.config import AppConfig
from app.core.dependencies import get_app_config


def get_token_secret(config: AppConfig = fastapi.Depends(get_app_config)) -> str:
    return config.TOKEN_SECRET


class JwtExpired(Exception):
    def __init__(self):
        super().__init__("token is expired")


class JwtInvalid(Exception):
    def __init__(self):
        super().__init__("token is invalid")


class JwtService:
    def __init__(
        self,
        secret: str = fastapi.Depends(get_token_secret),
    ) -> None:
        super().__init__()
        assert isinstance(secret, str), "secret is required"
        self.secret = secret

    def create_token(
        self,
        content: typing.Any,
        expires_in: int,
        now: datetime.datetime | None = None,
    ) -> tuple[str, datetime.datetime]:
        issued_at = now or datetime.datetime.now(tz=datetime.UTC).replace(microsecond=0)
        expires_at = issued_at + datetime.timedelta(seconds=expires_in)
        payload = {
            **content,
            "exp": expires_at,
            "iat": issued_at,
        }
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return token, expires_at

    def validate_token(
        self,
        token: str,
    ) -> dict[str, typing.Any]:
        try:
            decoded = jwt.decode(token, self.secret, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError as e:
            raise JwtExpired() from e
        except jwt.InvalidTokenError as e:
            raise JwtInvalid() from e
