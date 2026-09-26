from app.application.dtos.user_dtos import UserInDTO, UserOutDTO
from app.domain.contracts.user.repositories import IUserRepository
from app.domain.contracts.user.servicies import IHashService
from app.domain.entities.user_entities import UserEntity
from app.domain.exceptions.user_exceptions import EmailAlreadyExistsException


class RegisterUserUseCase:
    def __init__(
        self, user_repo: IUserRepository, hash_service: IHashService
    ) -> None:
        self.user_repo = user_repo
        self.hash_service = hash_service

    async def execute(self, data: UserInDTO):
        if await self.user_repo.verify_exists_email(data.email):
            raise EmailAlreadyExistsException()

        password_hashed = self.hash_service.hash(data.password)

        user = UserEntity(
            name=data.name, email=data.email, password=password_hashed
        )

        await self.user_repo.save(user=user)
        return UserOutDTO.from_domain(user)
