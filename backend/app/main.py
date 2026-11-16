"""FastAPI application entry point.

Authority
---------
``docs/specs/DEPLOYMENT.md`` §7.1 (health endpoints) and §7.2 (logging and
correlation).  The ASGI target is ``app.main:app`` (§2.3).

Related
-------
WBS P0-T02 — FastAPI skeleton and configuration.

Scope
-----
This module provides the liveness probe only.  ``/health/ready`` checks
PostgreSQL, the active rule set, the object store and the worker pool; none
of those exist yet, so the endpoint is deliberately **not** stubbed — a
readiness probe that cannot fail is worse than no probe at all
(``docs/specs/TESTING.md`` §1.6).  It is delivered with the dependencies it
must report on.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.v1.payroll import router as payroll_router
from app.api.v1.valuation import router as valuation_router
from app.core.config import Settings, get_settings
from app.core.logging import (
    configure_logging,
    get_logger,
    reset_correlation_id,
    set_correlation_id,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the ASGI application.

    ``APP_ENV`` and ``APP_DEBUG`` drive the behaviour of this function; no
    code change is needed to move a deployment between environments.
    """
    resolved = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
        configure_logging(resolved)
        logger = get_logger("app.main")
        logger.info(
            "application_starting",
            extra={"app_env": resolved.app_env, "app_debug": resolved.app_debug},
        )
        yield
        logger.info("application_stopping")

    application = FastAPI(
        title="Pish Hesabdari (پیش‌حسابداری)",
        version="0.1.0",
        debug=resolved.app_debug,
        docs_url="/docs" if resolved.app_debug else None,
        redoc_url="/redoc" if resolved.app_debug else None,
        openapi_url="/openapi.json" if resolved.app_debug else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.allowed_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-Id"],
        expose_headers=["X-Request-Id"],
    )

    @application.middleware("http")
    async def correlation_id_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Carry ``X-Request-Id`` through every log line and back to the client."""
        logger = get_logger("app.main.request")
        correlation_id = request.headers.get("X-Request-Id") or uuid4().hex
        token = set_correlation_id(correlation_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={"method": request.method, "path": request.url.path},
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            response.headers["X-Request-Id"] = correlation_id
            return response
        finally:
            # The correlation id must stay bound while the line above is
            # written; resetting it afterwards would log "-".
            reset_correlation_id(token)

    application.include_router(payroll_router)
    application.include_router(valuation_router)

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return the one stable error shape for every refusal.

        FastAPI's default validation body echoes the rejected input.  On this
        API the input is a salary package, so the echo would place a
        monetary amount inside an error response - the one thing the error
        contract forbids.  Only the field path and the failure type are
        reported.
        """
        problems = [
            f"{'.'.join(str(part) for part in error.get('loc', ()))}: {error.get('type', 'invalid')}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "PAYROLL_REQUEST_INVALID",
                    "detail": "; ".join(problems) or "the request is not valid",
                }
            },
        )

    @application.get("/health/live", tags=["health"], summary="Liveness probe")
    async def health_live() -> dict[str, str]:
        """Return 200 for as long as the process is running.

        No dependency is checked.  A failing dependency must not put the
        process into a restart loop (``docs/specs/DEPLOYMENT.md`` §7.1).
        """
        return {"status": "alive"}

    return application


app = create_app()
