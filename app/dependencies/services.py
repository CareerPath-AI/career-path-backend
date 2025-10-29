from fastapi import Depends
from app.services.user_services import UserService
from app.dependencies.repositories import get_user_repository
from app.repository.user_repository import UserRepository


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)