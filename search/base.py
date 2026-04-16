from abc import ABC, abstractmethod


class BaseSearchEngine(ABC):
#   Возвращает список URL по списку поисковых тем.
    @abstractmethod
    def search(self, topics: list[str]) -> list[str]:
        pass