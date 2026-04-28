from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import is_token_blacklisted
from app.dependencies.database import get_db
from app.utils.token_utils import decode_jwt_token
from jose import JWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-form")


async def verify_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        # Verifica se o token ta na blacklist
        if await is_token_blacklisted(token, db):
            raise HTTPException(
                status_code=401,
                detail="Token revoked"
            )
        
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Não foi possível validar as credenciais",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token é inválido ou está expirado")
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
