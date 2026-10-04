from datetime import datetime
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase

from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.email_message.status_message import StatusEmailMessage

from .email_account_model import EmailAccount


class EmailMessage(UUIDAuditBase):
    __tablename__ = 'email_messages'

    to_address: Mapped[str] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    email_account_id: Mapped[UUID] = mapped_column(ForeignKey('email_accounts.id'))
    email_account: Mapped['EmailAccount'] = relationship('EmailAccount', lazy='joined')
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[StatusEmailMessage] = mapped_column(SQLEnum(StatusEmailMessage, native_enum=False), nullable=False)
    sent_as: Mapped[datetime] = mapped_column(nullable=True) 
