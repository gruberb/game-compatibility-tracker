from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper

class PCGamerScraper(BaseScraper):
    name = 'PCGamer'

    def scrape(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        url = 'https://www.pcgamer.com/games/the-top-100-pc-games-2024/'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        entries = soup.find_all('h2', id=re.compile(r'\d+-.*'))

        for entry in entries:
            text = entry.text.strip()
            match = re.match(r'(\d+)\.\s+(.+)', text)
            if match:
                rank = int(match.group(1))
                title = match.group(2)
                games.append({
                    'rank': rank,
                    'title': title,
                    'source': 'PCGamer'
                })

        return games
