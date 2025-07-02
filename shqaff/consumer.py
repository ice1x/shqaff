from abc import ABC, abstractmethod


class Consumer(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def run(self, payload: dict) -> None:
        pass
