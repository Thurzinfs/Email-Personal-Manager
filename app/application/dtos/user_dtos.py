from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserInDTO(BaseModel):
    name: str
    email: str
    password: str


class UserOutDTO(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, model):
        return cls(
            id=model.id,
            name=model.name,
            email=model.email,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
