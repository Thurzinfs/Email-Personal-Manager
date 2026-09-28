from pydantic import BaseModel

from app.application.dtos.auth_dtos import (
    LoginInDTO,
    LoginOutDTO,
    RequestRefreshTokenInDTO,
)


class LoginInSchema(BaseModel):
    email: str
    password: str

    def to_dto(self) -> LoginInDTO:
        return LoginInDTO(email=self.email, password=self.password)


class LoginOutSchema(BaseModel):
    access_token: str
    refresh_token: str

    @staticmethod
    def from_domain(dto: LoginOutDTO):
        return LoginOutSchema(
            access_token=dto.access_token, refresh_token=dto.refresh_token
        )


class RequestRefreshTokenInSchema(BaseModel):
    refresh_token: str

    def to_dto(self) -> RequestRefreshTokenInDTO:
        return RequestRefreshTokenInDTO(refresh_token=self.refresh_token)
