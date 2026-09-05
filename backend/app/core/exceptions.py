from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger("exceptions")


class ErrorItem(BaseModel):
    field: str | None = None
    message: str


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    errors: list[ErrorItem] | None = None


class AppException(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_type: str = "bad-request",
        title: str = "Requisição inválida",
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.error_type = f"https://finapp.dev/errors/{error_type}"
        self.title = title
        self.errors = list(errors) if errors else None


class UnauthorizedException(AppException):
    def __init__(
        self,
        detail: str = "Credenciais inválidas ou token expirado",
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="unauthorized",
            title="Não autorizado",
            errors=errors,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        detail: str = "Acesso proibido",
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="forbidden",
            title="Acesso negado",
            errors=errors,
        )


class EntityNotFoundException(AppException):
    def __init__(
        self,
        entity_name: str,
        identifier: Any = None,
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        detail = (
            f"{entity_name} não encontrado(a)"
            if identifier is None
            else f"{entity_name} com identificador '{identifier}' não encontrado(a)"
        )
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="not-found",
            title="Recurso não encontrado",
            errors=errors,
        )


class ConflictException(AppException):
    def __init__(
        self,
        detail: str = "Conflito com o estado atual do recurso",
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_type="conflict",
            title="Conflito de dados",
            errors=errors,
        )


class ValidationException(AppException):
    def __init__(
        self,
        detail: str = "Um ou mais campos são inválidos",
        errors: Sequence[ErrorItem] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="validation-error",
            title="Erro de validação",
            errors=errors,
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            "app_exception",
            path=request.url.path,
            status=exc.status_code,
            detail=exc.detail,
        )
        problem = ProblemDetails(
            type=exc.error_type,
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            ErrorItem(
                field=".".join(str(loc) for loc in err["loc"] if loc != "body"),
                message=err["msg"],
            )
            for err in exc.errors()
        ]
        logger.warning(
            "validation_error",
            path=request.url.path,
            errors=errors,
        )
        problem = ProblemDetails(
            type="https://finapp.dev/errors/validation-error",
            title="Erro de validação",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Um ou mais campos são inválidos",
            errors=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        problem = ProblemDetails(
            type="https://finapp.dev/errors/http-error",
            title="Erro HTTP",
            status=exc.status_code,
            detail=str(exc.detail),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            exc_info=exc,
        )
        problem = ProblemDetails(
            type="https://finapp.dev/errors/internal-server-error",
            title="Erro interno do servidor",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno inesperado no servidor.",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=problem.model_dump(exclude_none=True),
        )
