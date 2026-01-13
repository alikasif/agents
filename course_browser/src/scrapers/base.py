from abc import ABC, abstractmethod
from typing import List
from ..models import Course
from ..browser import BrowserManager

class BaseScraper(ABC):
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Course]:
        pass

    @abstractmethod
    async def get_details(self, course: Course) -> Course:
        pass
