from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.core.security import bcrypt_context, create_token, add_token_to_blacklist
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.schemas.auth_schema import MessageResponse, TokenResponse, RefreshTokenResponse
from datetime import timedelta
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user_account(self, user_data: RegisterRequest) -> MessageResponse:
        if await self.user_repository.email_exists(user_data.email):
            raise HTTPException(status_code=400, detail="Esse email já está em uso")
        
        crypted_password = bcrypt_context.hash(user_data.password)
        
        await self.user_repository.create(
            name=user_data.name,
            email=user_data.email,
            password_hash=crypted_password
        )
        
        return MessageResponse(message="Usuário criado com sucesso")

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repository.get_by_email(email)
        
        if not user or not bcrypt_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Credenciais inválidas",
            )
        
        return user

    async def login(self, login_schema: LoginRequest) -> TokenResponse:
        user = await self.authenticate_user(login_schema.email, login_schema.password)

        access_token = create_token(user.id)
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))
        
        return TokenResponse(
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type="Bearer"
        )

    async def login_form(self, form_data: OAuth2PasswordRequestForm) -> TokenResponse:
        user = await self.authenticate_user(form_data.username, form_data.password)

        access_token = create_token(user.id)
        return TokenResponse(
            access_token=access_token, 
            refresh_token="", 
            token_type="Bearer"
        )

    async def use_refresh_token(self, user: User) -> RefreshTokenResponse:
        access_token = create_token(user.id)
        return RefreshTokenResponse(access_token=access_token, token_type="Bearer")

    async def logout(self, request: Request, current_user: User) -> MessageResponse:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token inválido")

        token = authorization.replace("Bearer ", "")
        
        # Note: add_token_to_blacklist precisa ser adaptado para usar repository
        await add_token_to_blacklist(token, self.user_repository.session)

        return MessageResponse(message="Logout realizado com sucesso")

    async def get_user_profile(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user