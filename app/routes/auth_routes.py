from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, MessageResponse, RefreshTokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.dependencies.security import verify_token
from app.models.user import User
from app.services.user_services import user_service


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/create", response_model=MessageResponse, status_code=201)
async def create_account(user_data: RegisterRequest, session: AsyncSession = Depends(get_db)):
    """
    Cria um novo usuário no banco de dados.
    """
    return await user_service.create_user_account(user_data, session)
    

@auth_router.post("/login", response_model=TokenResponse)
async def login(login_schema: LoginRequest, session: AsyncSession = Depends(get_db)):
    """
    Autentica usuários no sistema.
    """
    return await user_service.login(login_schema, session)


@auth_router.post("/login-form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    return await user_service.login_form(form_data, session)


@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def use_refresh_token(user: User = Depends(verify_token)):
    """
    Rota para gerar novo access token
    """
    return await user_service.use_refresh_token(user)


@auth_router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Faz logout do usuário adicionando o token à blacklist
    """
    return await user_service.logout(request, current_user, db)
