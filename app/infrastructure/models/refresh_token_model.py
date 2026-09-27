from datetime import datetime
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user_models import User


class RefreshToken(UUIDAuditBase):
    __tablename__ = 'refresh_tokens'

    user_id: Mapped[UUID] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship("User", lazy='joined')
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expire_at: Mapped[datetime]
    revoked: Mapped[bool] = mapped_column(default=False)
