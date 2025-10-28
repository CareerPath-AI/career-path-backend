from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import bcrypt_context
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.schemas.auth_schema import MessageResponse, TokenResponse, RefreshTokenResponse
from app.core.security import authenticate_user, create_token, add_token_to_blacklist
from datetime import timedelta


class UserService:
    async def create_user_account(self, user_data: RegisterRequest, session: AsyncSession):
        """
        Serviço que cria um novo usuário no banco de dados.
        """
        result = await session.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()
        if user:
            # Usuário com esse email já existe no banco
            raise HTTPException(status_code=400, detail="Esse email já está em uso")
        else:
            crypted_password = bcrypt_context.hash(user_data.password)
            new_user = User(user_data.name, user_data.email, crypted_password)
            session.add(new_user)
            await session.commit()
            return MessageResponse(message="Usuário criado com sucesso")

    async def login(self, login_schema: LoginRequest, session: AsyncSession):
        """
        Serviço que autentica usuários no sistema.
        """
        user = await authenticate_user(login_schema.email, login_schema.password, session)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Usuário não encontrado ou credenciais inválidas",
            )

        access_token = create_token(user.id)
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))
        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
        )

    async def login_form(self, form_data: OAuth2PasswordRequestForm, session: AsyncSession):
        """
        Serviço para login no swagger
        """
        user = await authenticate_user(form_data.username, form_data.password, session)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Usuário não encontrado ou credenciais inválidas",
            )

        access_token = create_token(user.id)
        return TokenResponse(
            access_token=access_token, refresh_token="", token_type="Bearer"
        )

    async def use_refresh_token(self, user: User):
        """
        Serviço para gerar novo access token
        """
        access_token = create_token(user.id)
        return RefreshTokenResponse(access_token=access_token, token_type="Bearer")

    async def logout(self, request: Request, current_user: User, db: AsyncSession):
        """
        Serviço de logout do usuário adicionando o token à blacklist.
        """
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token inválido")

        token = authorization.replace("Bearer ", "")

        # Adiciona a blacklist
        await add_token_to_blacklist(token, db)

        return MessageResponse(message="Logout realizado com sucesso")


user_service = UserService()
