from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup, Tag
import re
from pathlib import Path

from .base import BaseScraper
from ..config import config

class GenericScraper(BaseScraper):
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.url = config['url']
        self.parser_config = config['parser_config']

    def find_element(self, soup: BeautifulSoup, config: Dict[str, Any]) -> List[Tag]:
        """Find elements based on configuration"""
        kwargs = {}

        # Handle class attributes
        if 'attributes' in config:
            kwargs.update(config['attributes'])

        # Handle ID pattern
        if 'id_pattern' in config:
            kwargs['id'] = re.compile(config['id_pattern'])

        return soup.find_all(config['tag'], **kwargs)

    def extract_title_and_rank(self, element: Tag, config: Dict[str, Any]) -> Optional[tuple]:
        """Extract title and rank based on configuration"""
        try:
            if config.get('from_container', False):
                text = element.text.strip()
            else:
                title_element = element
                if config.get('find_next', False):
                    title_element = element.find_next(
                        config['tag'],
                        **(config.get('attributes', {}))
                    )
                text = title_element.text.strip()

            if 'pattern' in config:
                match = re.match(config['pattern'], text)
                if match:
                    rank = int(match.group(config['rank_group']))
                    title = match.group(config['title_group'])
                    return title, rank
            else:
                return text, None

        except (AttributeError, IndexError) as e:
            print(f"Error extracting title and rank: {e}")
            return None

    def scrape(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape website based on configuration"""
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            games = []

            # Find all container elements
            containers = self.find_element(soup, self.parser_config['container'])

            for container in containers:
                # Extract title and rank based on configuration
                if self.parser_config.get('rank_from_container', False):
                    rank = int(container.text.strip())
                    title_config = self.parser_config['title']
                    title_element = container.find_next(
                        title_config['tag'],
                        **(title_config.get('attributes', {}))
                    )
                    if title_element:
                        title = title_element.text.strip()
                        result = (title, rank)
                    else:
                        continue
                else:
                    result = self.extract_title_and_rank(
                        container,
                        self.parser_config['title']
                    )

                if result:
                    title, rank = result
                    games.append({
                        'rank': rank,
                        'title': title,
                        'source': self.name
                    })

            return games

        except Exception as e:
            print(f"Error scraping {self.name}: {e}")
            return []

class ScraperFactory:
    @staticmethod
    def load_scrapers() -> List[BaseScraper]:
        """Load scraper configurations and create scraper instances"""
        try:
            scraper_config = config.get_scraper_config()
            scrapers = []

            if 'scrapers' in scraper_config:
                for scraper_conf in scraper_config['scrapers']:
                    scrapers.append(GenericScraper(scraper_conf))

            return scrapers

        except Exception as e:
            print(f"Error loading scraper configurations: {e}")
            return []
