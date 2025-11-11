from fastapi import APIRouter, Depends
from app.schemas.user_schema import (
    MessageResponse,
    UserCreateRequest,
    UserUpdateRequest,
    UserUpdateResponse,
    UserDeleteRequest,
    UserGetResponse
)
from app.services.user_services import UserService
from app.dependencies.security import verify_token
from app.models.user import User
from app.dependencies.services import get_user_service


user_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@user_router.post("/", response_model=MessageResponse, status_code=201)
async def create_account(
    user_data: UserCreateRequest, user_service: UserService = Depends(get_user_service)
):
    """
    Cria um novo usuário no banco de dados.
    """
    return await user_service.create_user_account(user_data)


@user_router.patch("/me", response_model=UserUpdateResponse)
async def update_user_data(
    user_data: UserUpdateRequest,
    current_user: User = Depends(verify_token),
    user_service: UserService = Depends(get_user_service),
):
    """
    Atualiza os dados do usuário.
    """
    return await user_service.update_user(user_data, current_user)


@user_router.delete("/me/delete", response_model=MessageResponse)
async def delete(
    user_data: UserDeleteRequest,
    current_user: User = Depends(verify_token),
    user_service: UserService = Depends(get_user_service),
):
    """
    Deleta o usuário.
    """
    return await user_service.delete_user(user_data, current_user)


@user_router.get("/me", response_model=UserGetResponse)
async def get_user_data(
    current_user: User = Depends(verify_token),
    user_service: UserService = Depends(get_user_service),
):
    """
    Retorna os dados do usuário.
    """
    return await user_service.retrieve_user_data(current_user)
