from abc import ABC, abstractmethod
from typing import Tuple
from uuid import UUID

from app.domain.entities.auth.refresh_token_entity import RefreshTokenEntity


class IRefreshTokenServices(ABC):
    @abstractmethod
    def hash_token(self, token: str) -> str:
        ...

    @abstractmethod
    def create_access_token(self, user: UUID) -> str:
        ...

    @abstractmethod
    def create_refresh_token(
        self, user: UUID
    ) -> Tuple[str, RefreshTokenEntity]:
        ...

    @abstractmethod
    def decode_token(self, hash: str) -> dict:
        ...
