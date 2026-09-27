from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user_use_cases import (
    ListUsersUseCase,
    RegisterUserUseCase,
    ResponseUserUseCase,
)
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.infrastructure.database.repositorys.user_repository import AdvancedUserRepository
from app.infrastructure.database.services.user_services import HashService
from app.infrastructure.database.sqlite.database import get_session


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> AdvancedUserRepository:
    return AdvancedUserRepository(session=session)


def get_hash_service() -> IHashService:
    return HashService()


def get_register_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
    hash_service: IHashService = Depends(get_hash_service),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo=user_repo, hash_service=hash_service)


def get_response_user_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> ResponseUserUseCase:
    return ResponseUserUseCase(user_repo=user_repo)


def get_list_users_use_case(
    user_repo: IUserRepository = Depends(get_user_repository),
) -> ListUsersUseCase:
    return ListUsersUseCase(user_repo=user_repo)


UserRepoDependencie = Annotated[IUserRepository, Depends(get_user_repository)]

RegisterUserUseCaseDependencie = Annotated[
    RegisterUserUseCase, Depends(get_register_user_use_case)
]

ResponseUserUseCaseDependencie = Annotated[
    ResponseUserUseCase, Depends(get_response_user_use_case)
]

ListUsersUseCaseDependencie = Annotated[
    ListUsersUseCase, Depends(get_list_users_use_case)
]
