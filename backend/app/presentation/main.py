from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.presentation.api.v1.routers.auth import (
    limiter,
)
from app.presentation.api.v1.routers.auth import (
    router as auth_router,
)
from app.presentation.api.v1.routers.health import (
    HealthResponse,
)
from app.presentation.api.v1.routers.health import (
    router as health_router,
)
from app.presentation.api.v1.routers.pluggy import (
    router as pluggy_router,
)
from app.presentation.api.v1.routers.webhooks import (
    router as webhooks_router,
)
from app.presentation.middlewares.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    # Setup structured logging
    setup_logging()

    app = FastAPI(
        title="Finnapp API",
        description="API Backend para controle financeiro pessoal e integração Open Finance.",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json",
    )

    # Register slowapi limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    # Custom request ID middleware
    app.add_middleware(RequestIdMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global RFC 7807 exception handlers
    register_exception_handlers(app)

    # Root health endpoint directly for container health checks
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Root health check",
    )
    async def root_health() -> HealthResponse:
        return HealthResponse(status="ok", environment=settings.ENV)

    # API v1 routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(pluggy_router, prefix="/api/v1")
    app.include_router(webhooks_router, prefix="/api/v1")
    # Also support /webhooks directly without prefix
    app.include_router(webhooks_router)

    return app


app = create_app()
