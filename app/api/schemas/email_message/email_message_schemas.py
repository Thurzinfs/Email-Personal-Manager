from datetime import datetime
from typing import Optional

from pydantic import AwareDatetime, BaseModel, EmailStr

from app.application.dtos.email_messages_dtos import EmailMessageInDTO, EmailMessageOutDTO


class EmailMessageInSchema(BaseModel):
    to: EmailStr
    subject: str
    body: str
    scheduled_at: AwareDatetime | None

    def to_dto(self) -> EmailMessageInDTO:
        return EmailMessageInDTO(
            to=str(self.to),
            subject=self.subject,
            body=self.body,
            scheduled_at=self.scheduled_at
        )


class EmailMessageOutSchema(BaseModel):
    to: str
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None
    status: str

    @staticmethod
    def from_domain(dto: EmailMessageOutDTO):
        return EmailMessageOutSchema(
            to=dto.to,
            subject=dto.subject,
            body=dto.body,
            scheduled_at=dto.scheduled_at,
            status=dto.status
        )
