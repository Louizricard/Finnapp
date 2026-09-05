from uuid import UUID

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    Request,
    Response,
    status,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.application.dto.auth_dto import (
    LoginRequestDto,
    RefreshTokenRequestDto,
    RegisterRequestDto,
)
from app.application.use_cases.auth.get_me import GetCurrentUserUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.auth.refresh import RefreshTokenUseCase
from app.application.use_cases.auth.register import RegisterUserUseCase
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.repositories.user_repository import UserRepository
from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    StatusResponse,
    TokenResponse,
    UserResponse,
)
from app.presentation.dependencies import (
    get_current_user_id,
    get_refresh_token_repository,
    get_user_repository,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])
limiter = Limiter(key_func=get_remote_address)
COOKIE_REFRESH_TOKEN_NAME = "finapp_refresh_token"


def _handle_web_cookie(
    response: Response,
    refresh_token: str,
    platform: str | None,
) -> None:
    if platform and platform.lower() == "web":
        response.set_cookie(
            key=COOKIE_REFRESH_TOKEN_NAME,
            value=refresh_token,
            httponly=True,
            secure=settings.ENV == "production",
            samesite="strict",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/api/v1/auth",
        )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuário único",
    description="Cria o usuário único do sistema protegido pelo SETUP_TOKEN.",
)
async def register(
    payload: RegisterRequest,
    response: Response,
    x_client_platform: str | None = Header(default=None),
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> TokenResponse:
    use_case = RegisterUserUseCase(user_repo, refresh_repo)
    result = await use_case.execute(
        RegisterRequestDto(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            setup_token=payload.setup_token,
        )
    )
    _handle_web_cookie(response, result.refresh_token, x_client_platform)
    return TokenResponse.model_validate(result.model_dump())


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuário",
    description="Autentica o usuário e retorna access token e refresh token. Limitado a 5 tentativas/min.",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    x_client_platform: str | None = Header(default=None),
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> TokenResponse:
    use_case = LoginUseCase(user_repo, refresh_repo)
    result = await use_case.execute(
        LoginRequestDto(
            email=payload.email,
            password=payload.password,
        )
    )
    _handle_web_cookie(response, result.refresh_token, x_client_platform)
    return TokenResponse.model_validate(result.model_dump())


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token",
    description="Renova access token através do refresh token e executa rotação segura.",
)
async def refresh(
    response: Response,
    payload: RefreshTokenRequest | None = None,
    x_client_platform: str | None = Header(default=None),
    cookie_token: str | None = Cookie(default=None, alias=COOKIE_REFRESH_TOKEN_NAME),
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> TokenResponse:
    token_str = (payload.refresh_token if payload else None) or cookie_token
    if not token_str:
        raise ValidationException("Refresh token não informado no corpo ou cookie")

    use_case = RefreshTokenUseCase(user_repo, refresh_repo)
    result = await use_case.execute(RefreshTokenRequestDto(refresh_token=token_str))
    _handle_web_cookie(response, result.refresh_token, x_client_platform)
    return TokenResponse.model_validate(result.model_dump())


@router.post(
    "/logout",
    response_model=StatusResponse,
    summary="Logout de usuário",
    description="Invalida o refresh token ativo.",
)
async def logout(
    response: Response,
    payload: LogoutRequest | None = None,
    cookie_token: str | None = Cookie(default=None, alias=COOKIE_REFRESH_TOKEN_NAME),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> StatusResponse:
    token_str = (payload.refresh_token if payload else None) or cookie_token
    if token_str:
        use_case = LogoutUseCase(refresh_repo)
        await use_case.execute(token_str)

    response.delete_cookie(
        key=COOKIE_REFRESH_TOKEN_NAME,
        path="/api/v1/auth",
    )
    return StatusResponse(status="ok")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Dados do usuário logado",
    description="Retorna as informações de perfil do usuário autenticado pelo JWT.",
)
async def get_me(
    current_user_id: UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    use_case = GetCurrentUserUseCase(user_repo)
    result = await use_case.execute(current_user_id)
    return UserResponse.model_validate(result.model_dump())
