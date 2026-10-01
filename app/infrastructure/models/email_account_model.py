from datetime import datetime
from typing import List
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from .user_models import User


class EmailAccount(UUIDAuditBase):
    __tablename__ = 'email_accounts'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', lazy='joined')
    provider: Mapped[str] = mapped_column(String(240))
    email_address: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(String(180))
    refresh_token: Mapped[str] = mapped_column(String(180))
    token_expire_at: Mapped[datetime]
    scopes: Mapped[str]
    connected: Mapped[bool]
    connected_at: Mapped[datetime]


class OAuthConnection(UUIDAuditBase):
    __tablename__ = 'oauth_connections'

    state: Mapped[str]
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    code_verifier: Mapped[str] 
    expire_at: Mapped[datetime]
