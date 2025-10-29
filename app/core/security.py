from app.core.config import settings
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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


async def is_token_blacklisted(token: str, db: AsyncSession) -> bool:
    """
    Verifica se o token está na blacklist
    """
    result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.token == token))
    blacklisted_token = result.scalar_one_or_none()
    return blacklisted_token is not None


async def add_token_to_blacklist(token: str, db: AsyncSession):
    """
    Adiciona token à blacklist
    """
    try:
        # Tenta decodificar o token para pegar a expiração real
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
    except JWTError:
        # Se o token é inválido ou expirado, usa expiração padrão
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    try:
        blacklisted_token = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        
        db.add(blacklisted_token)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        print(f"Erro ao adicionar token à blacklist: {e}")


async def authenticate_user(email: str, password: str, session: AsyncSession):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password_hash):
        return False
    
    return user
