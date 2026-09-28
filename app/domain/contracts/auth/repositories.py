from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.auth.refresh_token_entity import RefreshTokenEntity


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def save(self, refresh: RefreshTokenEntity) -> RefreshTokenEntity:
        ...

    @abstractmethod
    async def find_by_hash(self, hash: str) -> RefreshTokenEntity | None:
        ...

    @abstractmethod
    async def list_tokens_by_user(
        self, user: UUID
    ) -> List[RefreshTokenEntity]:
        ...
