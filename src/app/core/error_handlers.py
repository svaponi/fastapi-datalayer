import logging

import fastapi
from asgi_correlation_id import correlation_id
from asyncpg_datalayer.errors import PoolOverflowException, TooManyConnectionsException
from starlette.exceptions import HTTPException as StarletteHTTPException


def setup_error_handlers(app: fastapi.FastAPI):
    _logger = logging.getLogger("app.exception")

    async def _handle_error(
        req: fastapi.Request,
        exc: Exception,
        status_code: int,
        message: str,
        **kwargs,
    ) -> fastapi.responses.JSONResponse:

        if status_code == 500:
            _logger.exception(exc)
        else:
            _logger.error(exc)

        request_id = correlation_id.get()

        body = {
            "status_code": status_code,
            "message": message,
            "request_id": request_id,
        }
        body.update(kwargs)
        return fastapi.responses.JSONResponse(body, status_code=status_code)

    async def _value_error_handler(
        req: fastapi.Request, exc: ValueError
    ) -> fastapi.responses.JSONResponse:
        return await _handle_error(
            req,
            exc,
            status_code=400,
            message=str(exc),
        )

    async def _internal_server_error_handler(
        req: fastapi.Request, exc: Exception
    ) -> fastapi.responses.JSONResponse:
        return await _handle_error(
            req,
            exc,
            status_code=500,
            message="Internal server error",
        )

    async def _internal_http_exception_handler(
        req: fastapi.Request, exc: StarletteHTTPException
    ) -> fastapi.responses.JSONResponse:
        return await _handle_error(
            req,
            exc,
            status_code=exc.status_code,
            message=exc.detail,
        )

    async def _too_many_requests_handler(
        req: fastapi.Request, exc: Exception
    ) -> fastapi.responses.JSONResponse:
        return await _handle_error(
            req,
            exc,
            status_code=429,
            message="too many requests",
        )

    app.add_exception_handler(ValueError, _value_error_handler)
    app.add_exception_handler(TooManyConnectionsException, _too_many_requests_handler)
    app.add_exception_handler(PoolOverflowException, _too_many_requests_handler)
    # Override starlette.exceptions.HTTPException response with our handler. Noe that fastapi.HTTPException inherits
    # from starlette.exceptions.HTTPException. See https://fastapi.tiangolo.com/tutorial/handling-errors
    app.add_exception_handler(StarletteHTTPException, _internal_http_exception_handler)
    # IMPORTANT: Defining an error_handler for 500 or `Exception` will end up as default error handler applied by
    # ServerErrorMiddleware, instead of ExceptionMiddleware (see Starlette.build_middleware_stack()).
    # This causes the handler to be called as last, specifically after our RequestContext middleware.
    # Therefore, the RequestContext has already been cleaned up and cannot be accessed in the error handler.
    app.add_exception_handler(Exception, _internal_server_error_handler)
