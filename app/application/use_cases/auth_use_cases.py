from uuid import UUID

from app.application.dtos.auth_dtos import LoginInDTO, LoginOutDTO
from app.domain.contracts.auth.repositories import IRefreshTokenRepository
from app.domain.contracts.auth.servicies import IRefreshTokenServices
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.domain.exceptions.user_exceptions import UserNotFoundException
from config.exception import BaseDomainException


class LoginUserUseCase:
    def __init__(self, auth_repo: IRefreshTokenRepository, auth_service: IRefreshTokenServices, user_repo: IUserRepository, hash_service: IHashService) -> None:
        self.auth_repo=auth_repo
        self.auth_service=auth_service
        self.user_repo=user_repo
        self.hash_service=hash_service

    async def execute(self, dto: LoginInDTO):
        user = await self.user_repo.find_by_email(dto.email)
        if not user:
            raise UserNotFoundException()

        if user.deleted_at is not None:
            raise UserNotFoundException()

        if not self.hash_service.verify(dto.password, user.password):
            raise BaseDomainException(message='Credentials invalid')

        access_token = self.auth_service.create_access_token(user.id)

        refresh_token, refresh_entity = self.auth_service.create_refresh_token(user.id)

        await self.auth_repo.save(refresh_entity)

        return LoginOutDTO(access_token=access_token, refresh_token=refresh_token)
