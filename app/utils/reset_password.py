from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from app.core.logging_config import logger

def create_reset_password_token(email: str):
    try:
        data = {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
        token = jwt.encode(data, settings.FORGET_PWD_SECRET_KEY, settings.ALGORITHM)
        return token
    except JWTError:
        logger.error("Falha ao gerar token de reset de senha")
