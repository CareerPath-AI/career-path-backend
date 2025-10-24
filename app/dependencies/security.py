from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import is_token_blacklisted
from app.dependencies.database import get_db
from jose import jwt, JWTError
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-form")


def verify_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        # Verifica se o token ta na blacklist
        if is_token_blacklisted(token, db):
            raise HTTPException(
                status_code=401,
                detail="Token revoked"
            )
        
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Não foi possível validar as credenciais",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token é inválido ou está expirado")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
    
