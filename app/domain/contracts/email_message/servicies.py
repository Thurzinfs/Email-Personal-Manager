from abc import ABC, abstractmethod

from app.domain.entities.email_message.email_message_entity import EmailMessageEntity


class IEmailMessageDispatcherService(ABC):
    @abstractmethod
    async def dispatch(self, message: EmailMessageEntity) -> None:
        ...
    