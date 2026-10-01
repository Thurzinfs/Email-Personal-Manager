from abc import ABC, abstractmethod
from uuid import UUID


class IGmailProviderAdapter(ABC):
    @abstractmethod
    async def get_service(self, email_account_id: UUID):
        ...

