from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseScraper(ABC):
    name: str

    @abstractmethod
    def scrape(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        pass

# Export the class
__all__ = ['BaseScraper']
