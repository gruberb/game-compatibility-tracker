from .base import BaseScraper
from .generic import GenericScraper, ScraperFactory

__all__ = ['BaseScraper', 'get_all_scrapers']

def get_all_scrapers():
    """Get all configured scrapers"""
    return ScraperFactory.load_scrapers()
