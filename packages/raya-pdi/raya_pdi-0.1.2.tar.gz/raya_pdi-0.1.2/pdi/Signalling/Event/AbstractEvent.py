from abc import ABC, abstractmethod


class Event(ABC):
    @classmethod
    @abstractmethod
    def getName(cls) -> str:
        pass
