from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class IGmailProviderAdapter(ABC):
    @abstractmethod
    async def get_service(self, email_account_id: UUID):
        ...

    @abstractmethod
    async def send_email(self, email_account_id: UUID, to: str, subject: str, body: Any):
        ...