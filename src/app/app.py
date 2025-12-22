import contextlib
import logging
import os
import typing

import fastapi
from asyncpg_datalayer.db_factory import create_db
from asyncpg_datalayer.migrationtool.main import apply_migrations
from starlette.responses import RedirectResponse

from app import migrations_dir
from app.api.api_factory import setup_api
from app.core.config import AppConfig
from app.core.correlation_id import setup_correlation_id
from app.core.cors import setup_cors
from app.core.error_handlers import setup_error_handlers
from app.core.logs import setup_logging
from app.email.email_client_factory import create_email_client


@contextlib.asynccontextmanager
async def _lifespan(app: "App"):
    app.logger.info(f"Starting 🔄")
    await apply_migrations(app.db.postgres_url, migrations_dir)
    # ...
    app.logger.info("Started ✅ ")
    yield
    app.logger.info("Shutting down 🔄")
    await app.db.disconnect()
    # ...
    app.logger.info("Shutdown 🛑")


class App(fastapi.FastAPI):
    def __init__(
        self,
        **extra: typing.Any,
    ) -> None:
        self.config = AppConfig()

        # IMPORTANT all logs previous to calling setup_logging will be not formatted
        setup_logging(self.config.log)
        self.logger = logging.getLogger(f"app")

        super().__init__(
            lifespan=_lifespan,
            title=f"{self.config.get_app_name()} API",
            description="[GitHub](https://github.com/zym-tools/zym-be)",
            version=self.config.VERSION,
            docs_url="/api/docs" if self.config.DOCS_ENABLED else None,
            openapi_url="/api/openapi.json" if self.config.DOCS_ENABLED else None,
            **extra,
        )

        # Setup ASGI Correlation ID middleware
        setup_correlation_id(self)

        # Http error handlers (equivalent to try block that can handle uncaught exceptions)
        setup_error_handlers(self)

        # Setup cors
        setup_cors(self, self.config.cors)

        # Setup API
        setup_api(self)

        self.db = create_db(os.environ)
        self.state.db = self.db
        self.email_client = create_email_client(self.config.email)

        if hasattr(self, "docs_url") and self.docs_url:

            @self.get("/", include_in_schema=False)
            def root():
                return RedirectResponse(self.docs_url)


def create_app():
    return App()
