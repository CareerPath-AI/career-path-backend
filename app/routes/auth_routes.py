from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest, 
    TokenResponse, 
    MessageResponse, 
    RefreshTokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.dependencies.security import verify_token
from app.models.user import User
from app.services.user_services import UserService
from app.dependencies.services import get_user_service


auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/register", response_model=MessageResponse, status_code=201)
async def create_account(
    user_data: RegisterRequest, user_service: UserService = Depends(get_user_service)
):
    """
    Cria um novo usuário no banco de dados.
    """
    return await user_service.create_user_account(user_data)


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_schema: LoginRequest, user_service: UserService = Depends(get_user_service)):
    """
    Autentica usuários no sistema.
    """
    return await user_service.login(login_schema)


@auth_router.post("/login-form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)):
    return await user_service.login_form(form_data)


@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def use_refresh_token(user: User = Depends(verify_token), user_service: UserService = Depends(get_user_service)):
    """
    Rota para gerar novo access token
    """
    return await user_service.use_refresh_token(user)


@auth_router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    """
    Faz logout do usuário adicionando o token à blacklist
    """
    return await user_service.logout(request, current_user)


@auth_router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request_data: ForgotPasswordRequest, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.forgot_user_password(request_data, background_tasks)


@auth_router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request_data: ResetPasswordRequest, user_service: UserService = Depends(get_user_service)):
    """
    Reseta a senha do usuário.
    """
    return await user_service.reset_user_password(request_data)
