from fastapi import Depends
from app.core.config import settings
from app.dependencies.database import get_db
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


def is_token_blacklisted(token: str, db: Session) -> bool:
    """
    Verifica se o token está na blacklist
    """
    blacklisted_token = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token
    ).first()
    return blacklisted_token is not None


def add_token_to_blacklist(token: str, db: Session):
    """
    Adiciona token à blacklist
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        blacklisted_token = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        db.add(blacklisted_token)
        db.commit()
    except JWTError:
        # Caso o token seja invalido, ainda assim adiciona a blacklist
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        blacklisted_token = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        db.add(blacklisted_token)
        db.commit()


def authenticate_user(email: str, password: str, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password_hash):
        return False
    
    return user