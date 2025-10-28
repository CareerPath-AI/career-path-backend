from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, MessageResponse, RefreshTokenResponse
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.security import verify_token
from app.core.security import bcrypt_context
from app.models.user import User
from app.core.security import authenticate_user, create_token, add_token_to_blacklist
from app.services.user_services import user_service
from datetime import timedelta


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/create", response_model=MessageResponse, status_code=201)
async def create_account(user_data: RegisterRequest, session: Session = Depends(get_db)):
    """
    Cria um novo usuário no banco de dados.
    """
    return user_service.create_user_account(user_data, session)
    

@auth_router.post("/login", response_model=TokenResponse)
async def login(login_schema: LoginRequest, session: Session = Depends(get_db)):
    """
    Autentica usuários no sistema.
    """
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Usuário não encontrado ou credenciais inválidas"
        )
    
    access_token = create_token(user.id)
    refresh_token = create_token(user.id, token_duration=timedelta(days=7))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )


@auth_router.post("/login-form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=400, detail="Usuário não encontrado ou credenciais inválidas"
        )

    access_token = create_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token="",
        token_type="Bearer"
    )

@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def use_refresh_token(user: User = Depends(verify_token)):
    """
    Rota para gerar novo access token
    """
    access_token = create_token(user.id)
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="Bearer"
    )


@auth_router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Faz logout do usuário adicionando o token à blacklist
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    token = authorization.replace("Bearer ", "")

    # Adiciona a blacklist
    add_token_to_blacklist(token, db)

    return MessageResponse(message="Logout realizado com sucesso")
