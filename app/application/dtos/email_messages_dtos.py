from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmailMessageInDTO(BaseModel):
    to: str
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None


class EmailMessageOutDTO(BaseModel):
    to: str
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None
    status: str

    @classmethod
    def from_domain(cls, model):
        return cls(
            to=model.to_address,
            subject=model.subject,
            body=model.body,
            scheduled_at=model.scheduled_at,
            status=model.status
        )
