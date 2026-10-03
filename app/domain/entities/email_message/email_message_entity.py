from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.entities.email_message.status_message import StatusEmailMessage
from app.domain.value_objects.scheduled_at_vo import ScheduledAtVO


@dataclass
class EmailMessageEntity:
    id: UUID = field(default_factory=uuid4)
    to_address: str = field(default='')
    subject: str = field(default='')
    body: str = field(default='')
    email_account: UUID | None = field(default=None)
    scheduled_at: ScheduledAtVO | None = field(default=None)
    status: StatusEmailMessage = field(default=StatusEmailMessage.PENDING)
    created_at: datetime = field(default_factory=datetime.now)
    sent_as: datetime | None = field(default=None)

    def mark_as_processing(self) -> None:
        self.status = StatusEmailMessage.PROCESSING

    def mark_as_sent(self) -> None:
        self.status = StatusEmailMessage.SENT
        self.sent_as = datetime.now(timezone.utc)

    def mark_as_failed(self) -> None:
        self.status = StatusEmailMessage.FAILED
