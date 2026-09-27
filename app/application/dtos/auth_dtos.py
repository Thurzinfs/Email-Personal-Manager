from pydantic import BaseModel


class LoginInDTO(BaseModel):
    email: str
    password: str


class LoginOutDTO(BaseModel):
    access_token: str
    refresh_token: str

    @classmethod
    def from_domain(cls, model):
        return cls(
            access_token=model.access_token,
            refresh_token=model.refresh_token
        )


class RequestRefreshTokenInDTO(BaseModel):
    refresh_token: str
