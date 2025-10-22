from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.database import get_db
from jose import jwt, JWTError
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-form")


def verify_token(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
