from abc import ABC, abstractmethod
import os

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()


class ITokenEncryptor(ABC):
    @abstractmethod
    def encrypt(self, token: str) -> str:
        ...

    @abstractmethod
    def decrypt(self, encrypted_token: str) -> str:
        ...


class TokenEncryptorSecurity(ITokenEncryptor):
    def __init__(self) -> None:
        self.chiper = Fernet(os.getenv('ENCRYPTION_KEY', ''))

    def encrypt(self, token: str) -> str:
        data_bytes = token.encode('utf-8')
        encrypted_bytes = self.chiper.encrypt(data_bytes)
        return encrypted_bytes.decode('utf-8')

    def decrypt(self, encrypted_token: str) -> str:
        try:
            token_bytes = encrypted_token.encode('utf-8')
            decrypted_bytes = self.chiper.decrypt(token_bytes)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            raise ValueError("O token informado é inválido ou a chave está incorreta.")
    