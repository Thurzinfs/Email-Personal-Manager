from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.application.dtos.user_dtos import UserInDTO, UserOutDTO


class BaseSchema(BaseModel):
    ...


class UserInSchema(BaseSchema):
    name: str
    email: EmailStr
    password: str

    def to_dto(self) -> UserInDTO:
        return UserInDTO(
            name=self.name, email=str(self.email), password=self.password
        )


class UserOutSchema(BaseSchema):
    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @staticmethod
    def from_domain(dto: UserOutDTO):
        return UserOutSchema(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            deleted_at=dto.deleted_at,
        )
