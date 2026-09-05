from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Retorna o status operacional da API.",
)
async def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(
        status="ok",
        environment=settings.ENV,
    )
