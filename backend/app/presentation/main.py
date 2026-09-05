from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.presentation.api.v1.routers.health import (
    HealthResponse,
)
from app.presentation.api.v1.routers.health import (
    router as health_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Finnapp API",
        description="API Backend para controle financeiro pessoal e integração Open Finance.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    return app


app = create_app()
