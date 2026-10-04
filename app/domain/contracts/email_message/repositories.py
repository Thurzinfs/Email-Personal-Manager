from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities.email_message.email_message_entity import EmailMessageEntity


class IEmailMessageRepository(ABC):
    @abstractmethod
    async def save(self, entity: EmailMessageEntity) -> EmailMessageEntity:
        ...

    @abstractmethod
    async def find_by_email_account(self, email_account: UUID) -> EmailMessageEntity | None:
        ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> EmailMessageEntity | None:
        ...

    @abstractmethod
    async def list_messages_by_email_account(self, email_account: UUID) -> List[EmailMessageEntity]:
        ...
