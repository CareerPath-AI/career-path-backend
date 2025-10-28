from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.core.security import bcrypt_context
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.schemas.auth_schema import MessageResponse, TokenResponse
from app.core.security import authenticate_user, create_token
from datetime import timedelta


class UserService():
    def create_user_account(self, user_data: RegisterRequest, session: Session = Depends(get_db)):
        """
        Serviço que cria um novo usuário no banco de dados.
        """
        user = session.query(User).filter(User.email == user_data.email).first()
        if user:
            # Usuário com esse email já existe no banco
            raise HTTPException(
                status_code=400, detail="Esse email já está em uso"
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
            return MessageResponse(message="Usuário criado com sucesso")
        
    
    def login(self, login_schema: LoginRequest, session: Session = Depends(get_db)):
        """
        Serviço que autentica usuários no sistema.
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
    



user_service = UserService()
