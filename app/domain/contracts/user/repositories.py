from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.user_entities import UserEntity


class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity:
        ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> UserEntity | None:
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        ...

    @abstractmethod
    async def list_users(self) -> List[UserEntity]:
        ...

    @abstractmethod
    async def verify_exists_email(self, email: str) -> bool:
        ...
