from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user_use_cases import RegisterUserUseCase
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.infrastructure.database.repository import AdvancedUserRepository
from app.infrastructure.database.service import HashService
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


UserRepoDependencie = Annotated[IUserRepository, Depends(get_user_repository)]
RegisterUserUseCaseDependencie = Annotated[
    RegisterUserUseCase, Depends(get_register_user_use_case)
]
