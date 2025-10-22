from fastapi import Depends
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.utils.password_utils import bcrypt_context
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt


def create_token(
    user_id, token_duration=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
):
    expire_date = datetime.now(timezone.utc) + token_duration
    dict_info = {
        "sub": str(user_id), 
        "exp": expire_date
    }
    encoded_jwt = jwt.encode(dict_info, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(email: str, password: str, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password_hash):
        return False
    
    return user