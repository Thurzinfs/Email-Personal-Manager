from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from app.domain.exceptions.gmail_account_exceptions import GmailAccountNotConnectedException


@dataclass
class EmailAccountEntity:
    id: UUID = field(default_factory=uuid4)
    user: UUID | None = field(default=None)
    provider: str = field(default='')
    email_address: str = field(default='')
    access_token: str = field(default='')
    refresh_token: str = field(default='')
    token_expire_at: datetime | None = field(default=None)
    scopes: List[str] = field(default_factory=list)
    connected: bool = field(default=False)
    connected_at: datetime | None = field(default=None)

    def refresh(self, new_access: str, new_expire: datetime) -> None:
        if not self.connected:
            raise GmailAccountNotConnectedException()

        self.access_token = new_access
        self.token_expire_at = new_expire


    def disconnect(self) -> None:
        self.connected = False
        self.access_token = ''
        self.refresh_token = ''


@dataclass
class OAuthConnectionEntity:
    state: str = field(default='')
    user_id: UUID | None = field(default=None)
    code_verifier: str = field(default='')
    created_at: datetime = field(default_factory=datetime.now)
    expire_at: datetime | None = field(default=None)

    def expire(self) -> None:
        self.expire_at = datetime.now()

    def is_expired(self) -> bool:
        if self.expire_at is None:
            return True
        
        return self.expire_at <= datetime.now(timezone.utc)
