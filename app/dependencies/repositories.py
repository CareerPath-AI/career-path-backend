from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repository import UserRepository
from app.dependencies.database import get_db


async def get_user_repository(
    session: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(session)