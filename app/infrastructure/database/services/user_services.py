from passlib.context import CryptContext

from app.domain.contracts.user.servicies import IHashService


class HashService(IHashService):
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=['bcrypt'])

    def hash(self, raw: str) -> str:
        return self.pwd_context.hash(raw)

    def verify(self, raw: str, hash: str) -> bool:
        return self.pwd_context.verify(raw, hash)
