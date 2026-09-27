from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.user.user_dependencies import get_hash_service, get_user_repository
from app.application.use_cases.auth_use_cases import LoginUserUseCase, LogoutUserUseCase
from app.domain.contracts.auth.repositories import IRefreshTokenRepository
from app.domain.contracts.auth.servicies import IRefreshTokenServices
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.infrastructure.database.repositorys.auth_repository import AdvancedRefreshTokenRepository
from app.infrastructure.database.services.auth_services import AuthTokenService
from app.infrastructure.database.sqlite.database import get_session


def get_auth_repository(session: AsyncSession = Depends(get_session)) -> AdvancedRefreshTokenRepository:
    return AdvancedRefreshTokenRepository(session=session)


def get_auth_service() -> IRefreshTokenServices:
    return AuthTokenService()


def get_auth_login_use_case(
    auth_service: IRefreshTokenServices = Depends(get_auth_service),
    auth_repo: IRefreshTokenRepository = Depends(get_auth_repository),
    hash_service: IHashService = Depends(get_hash_service),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> LoginUserUseCase:
    return LoginUserUseCase(
        auth_repo=auth_repo,
        auth_service=auth_service,
        hash_service=hash_service,
        user_repo=user_repo
    )


def get_auth_logout_use_case(
    auth_repo: IRefreshTokenRepository = Depends(get_auth_repository),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> LogoutUserUseCase:
    return LogoutUserUseCase(
        user_repo=user_repo,
        auth_repo=auth_repo
    )


LoginUserUseCaseDependencie = Annotated[LoginUserUseCase, Depends(get_auth_login_use_case)]
LogoutUserUseCaseDependencie = Annotated[LogoutUserUseCase, Depends(get_auth_logout_use_case)]
