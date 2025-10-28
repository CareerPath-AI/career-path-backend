from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.core.security import bcrypt_context
from app.schemas.auth_schema import RegisterRequest
from app.schemas.auth_schema import MessageResponse


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

user_service = UserService()
