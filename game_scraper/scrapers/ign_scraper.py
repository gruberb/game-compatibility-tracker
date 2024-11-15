from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper

class IGNScraper(BaseScraper):
    name = 'IGN'

    def scrape(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        url = 'https://www.ign.com/articles/the-best-100-video-games-of-all-time'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        game_entries = soup.find_all('h2', {'class': 'title2', 'data-cy': 'title2'})

        for entry in game_entries:
            strong_tag = entry.find('strong')
            if strong_tag:
                text = strong_tag.text.strip()
                match = re.match(r'(\d+)\.\s+(.+)', text)
                if match:
                    rank = int(match.group(1))
                    title = match.group(2)
                    games.append({
                        'rank': rank,
                        'title': title,
                        'source': 'IGN'
                    })

        return games
