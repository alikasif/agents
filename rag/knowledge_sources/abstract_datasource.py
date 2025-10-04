
from typing import List
from abc import ABC, abstractmethod

class AbstractDataSource(ABC):

    @abstractmethod
    def search(self, query: str) -> List[str]:
        """Search the knowledge source and return relevant documents."""
        pass

    @abstractmethod
    def about(self) -> str:
        pass

    @abstractmethod
    def short_name(self) -> str:
        pass
