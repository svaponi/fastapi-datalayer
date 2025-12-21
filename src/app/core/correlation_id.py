from uuid import uuid4

import fastapi
from asgi_correlation_id import CorrelationIdMiddleware


# See https://github.com/snok/asgi-correlation-id
# See https://medium.com/@sondrelg_12432/setting-up-request-id-logging-for-your-fastapi-application-4dc190aac0ea


def setup_correlation_id(app: fastapi.FastAPI) -> None:
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name="x-request-id",
        update_request_header=True,
        generator=lambda: uuid4().hex,
        # default validator allows only uuid-like strings, we want to allow any non-empty string
        validator=lambda x: x,
        transformer=lambda a: a,
    )
