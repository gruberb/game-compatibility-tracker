from typing import List, Type
from .base_scraper import BaseScraper
import pkgutil
import importlib

def get_all_scrapers() -> List[Type[BaseScraper]]:
    """Dynamically load all scraper classes that inherit from BaseScraper."""
    scrapers = []
    package = __name__
    prefix = package + '.'

    for _, module_name, _ in pkgutil.iter_modules(__path__, prefix):
        module = importlib.import_module(module_name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseScraper) and attr is not BaseScraper:
                scrapers.append(attr)
    return scrapers

__all__ = ['BaseScraper', 'get_all_scrapers']
