from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class RefreshTokenEntity:
    id: UUID = field(default_factory=uuid4)
    user: UUID | None = field(default=None)
    token_hash: str = field(default='')
    expire_at: datetime | None = field(default=None)
    created_at: datetime = field(default_factory=datetime.now)
    revoked: bool = field(default=False)

    def is_valid(self) -> bool:
        if self.expire_at is None:
            return True

        return not self.revoked and self.expire_at > datetime.now(timezone.utc)

    def revoke(self) -> None:
        self.revoked = True
