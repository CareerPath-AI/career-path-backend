from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user_schema import UserRegisterSchema
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.password_utils import bcrypt_context


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/create")
async def create_account(user_data: UserRegisterSchema, session: Session = Depends(get_db)):
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