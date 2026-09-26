from abc import ABC, abstractmethod


class IHashService(ABC):
    @abstractmethod
    def hash(self, raw: str) -> str:
        ...

    @abstractmethod
    def verify(self, raw: str, hash: str) -> bool:
        ...
