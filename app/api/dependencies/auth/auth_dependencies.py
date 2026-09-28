from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.user.user_dependencies import (
    get_hash_service,
    get_user_repository,
)
from app.application.dtos.user_dtos import UserOutDTO
from app.application.use_cases.auth_use_cases import (
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
)
from app.domain.contracts.auth.repositories import IRefreshTokenRepository
from app.domain.contracts.auth.servicies import IRefreshTokenServices
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.domain.entities.user.user_entities import UserEntity
from app.infrastructure.database.repositorys.auth_repository import (
    AdvancedRefreshTokenRepository,
)
from app.infrastructure.database.services.auth_services import AuthTokenService
from app.infrastructure.database.sqlite.database import get_session
from config import settings


def get_auth_repository(
    session: AsyncSession = Depends(get_session),
) -> AdvancedRefreshTokenRepository:
    return AdvancedRefreshTokenRepository(session=session)


def get_auth_service() -> IRefreshTokenServices:
    return AuthTokenService()


def get_auth_login_use_case(
    auth_service: IRefreshTokenServices = Depends(get_auth_service),
    auth_repo: IRefreshTokenRepository = Depends(get_auth_repository),
    hash_service: IHashService = Depends(get_hash_service),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        auth_repo=auth_repo,
        auth_service=auth_service,
        hash_service=hash_service,
        user_repo=user_repo,
    )


def get_auth_logout_use_case(
    auth_repo: IRefreshTokenRepository = Depends(get_auth_repository),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> LogoutUserUseCase:
    return LogoutUserUseCase(user_repo=user_repo, auth_repo=auth_repo)


def get_refresh_token_use_case(
    auth_repo: IRefreshTokenRepository = Depends(get_auth_repository),
    auth_service: IRefreshTokenServices = Depends(get_auth_service),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(auth_repo=auth_repo, auth_service=auth_service)


async def get_current_user(
    access_token: Annotated[
        str | None, Cookie(include_in_schema=False)
    ] = None,
    user_repo: IUserRepository = Depends(get_user_repository),
) -> UserEntity:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuario não autenticado.',
        )

    token_str = (
        access_token.replace('Bearer ', '')
        if access_token.startswith('Bearer ')
        else access_token
    )

    try:
        payload = jwt.decode(
            token_str,
            settings.settings.SECRET_KEY,
            algorithms=[settings.settings.ALGORITHM],
        )
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Tipo de token invalido.',
            )
        user_id = payload.get('sub', '')

    except jwt.PyJWKError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token invalido ou expirado.',
        )

    user = await user_repo.find_by_id(user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuario inativo ou nao encontrado.',
        )

    return user


LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, Depends(get_auth_login_use_case)
]
LogoutUserUseCaseDependency = Annotated[
    LogoutUserUseCase, Depends(get_auth_logout_use_case)
]
RefreshTokenUseCaseDependency = Annotated[
    RefreshTokenUseCase, Depends(get_refresh_token_use_case)
]

CurrentUserDependency = Annotated[UserEntity, Depends(get_current_user)]
