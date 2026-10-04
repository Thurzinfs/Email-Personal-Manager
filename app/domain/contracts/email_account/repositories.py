from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.email_account.emai_account_entity import EmailAccountEntity
from app.domain.entities.email_account.emai_account_entity import OAuthConnectionEntity


class IEmailAccountRepository(ABC):
    @abstractmethod
    async def save(self, entity: EmailAccountEntity) -> EmailAccountEntity:
        ...

    @abstractmethod
    async def find_by_user_id(self, id: UUID) -> EmailAccountEntity | None:
        ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> EmailAccountEntity | None:
        ...


class IOAuthConnectionRepository(ABC):
    @abstractmethod
    async def save(self, entity: OAuthConnectionEntity) -> OAuthConnectionEntity:
        ...

    @abstractmethod
    async def find_by_state(self, state: str) -> OAuthConnectionEntity | None:
        ...

    @abstractmethod
    async def delete_by_state(self, state: str) -> None:
        ...
