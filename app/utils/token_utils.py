from fastapi import HTTPException
from app.models.token_blacklist import TokenBlacklist
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from jose import jwt, JWTError
from app.core.config import settings


def cleanup_expired_tokens(db: Session) -> int:
    """
    Remove tokens expirados da blacklist
    """
    now = datetime.now(timezone.utc)
    deleted_count = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at < now
    ).delete()
    db.commit()
    return deleted_count


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token é inválido ou está expirado")
