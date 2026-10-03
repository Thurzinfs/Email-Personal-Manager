from datetime import datetime
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .email_account_model import EmailAccount


class EmailMessage(UUIDAuditBase):
    __tablename__ = 'email_messages'

    to_address: Mapped[str] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    email_account_id: Mapped[UUID] = mapped_column(ForeignKey('email_accounts.id'))
    email_account: Mapped['EmailAccount'] = relationship('EmailAccount', lazy='joined')
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status = Mapped[str]
    sent_as: Mapped[datetime] = mapped_column(nullable=True) 
