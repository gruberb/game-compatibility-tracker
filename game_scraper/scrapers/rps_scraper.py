from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class RPSScraper(BaseScraper):
    name = 'RockPaperShotgun'

    def scrape(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        url = 'https://www.rockpapershotgun.com/the-rps-100-2024'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        game_entries = soup.find_all('span', class_='top-video-game-pill')

        for entry in game_entries:
            name_span = entry.find_next('span', class_='top-video-game-name')
            if name_span:
                games.append({
                    'rank': int(entry.text.strip()),
                    'title': name_span.text.strip(),
                    'source': 'RPS'
                })

        return games
