from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class UserEntity:
    id: UUID = field(default_factory=uuid4)
    name: str = field(default='')
    email: str = field(default='')
    password: str = field(default='')
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = field(default=None)
    deleted_at: datetime | None = field(default=None)

    def change_name(self, new_name: str) -> None:
        self.name = new_name

    def change_email(self, new_email: str) -> None:
        self.email = new_email

    def change_password(self, new_hash_password: str) -> None:
        self.password = new_hash_password

    def delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
