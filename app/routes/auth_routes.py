from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schema import UserRegisterSchema
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.security import verify_token
from app.core.security import bcrypt_context
from app.models.user import User
from app.schemas.user_schema import UserLoginSchema
from app.core.security import authenticate_user, create_token
from datetime import timedelta


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/create")
async def create_account(user_data: UserRegisterSchema, session: Session = Depends(get_db)):
    """
    Cria um novo usuário no banco de dados.
    """
    user = session.query(User).filter(User.email == user_data.email).first()
    if user:
        # Usuario com esse email ja existe
        raise HTTPException(
            status_code=400, detail="Email já está em uso"
        )
    else:
        crypted_password = bcrypt_context.hash(user_data.password)
        new_user = User(
            user_data.name,
            user_data.email,
            crypted_password
        )
        session.add(new_user)
        session.commit()
        return {"message": "Usuário cadastrado com sucesso"}
    

@auth_router.post("/login")
async def login(login_schema: UserLoginSchema, session: Session = Depends(get_db)):
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
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@auth_router.post("/login-form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=400, detail="Usuário não encontrado ou credenciais inválidas"
        )

    access_token = create_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }


@auth_router.post("/refresh")
async def use_refresh_token(user: User = Depends(verify_token)):
    """
    Rota para gerar novo access token
    """
    access_token = create_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }