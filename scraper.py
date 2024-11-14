import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re
import time
import os

class GameScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_dir = Path('docs/data')
        self.cache_dir = Path('cache')
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        # Roman numeral mapping
        self.roman_to_arabic = {
            'I': '1',
            'II': '2',
            'III': '3',
            'IV': '4',
            'V': '5',
            'VI': '6',
            'VII': '7',
            'VIII': '8',
            'IX': '9',
            'X': '10'
        }

        # Common title variations
        self.title_variations = {
            'and': '&',
            'episode': 'ep',
            'episodes': 'ep',
            'part': '',
            'chapter': 'ch',
        }

        # Load Steam games list
        self.steam_games = self.get_steam_games_list()

    def normalize_title(self, title):
        """Normalize game title to improve matching"""
        # Remove content in parentheses
        title = re.sub(r'\s*\([^)]*\)', '', title)

        # Remove common suffixes
        title = title.replace(' Review', '').replace(' Multiplayer', '')

        # Additional game-specific normalizations
        special_cases = {
            'god of war (2018)': 'god of war',
            'the sims 4': 'the sims™ 4',  # Steam uses trademark symbol
            'hunt: showdown': 'hunt showdown',  # Steam doesn't use colon
            'homeworld: cataclysm': 'homeworld cataclysm',
            'titanfall 2': 'titanfall® 2',  # Steam uses registered trademark
            'hades 2': 'hades ii',  # Early Access games might use roman numerals
        }

        # Check special cases (case insensitive)
        lower_title = title.lower()
        if lower_title in special_cases:
            return special_cases[lower_title]

        # Split title into words
        words = title.split()

        # Process each word
        for i, word in enumerate(words):
            # Check for Roman numerals
            if word in self.roman_to_arabic:
                words[i] = self.roman_to_arabic[word]
            # Check for Roman numerals with colon
            elif ':' in word and word.replace(':', '') in self.roman_to_arabic:
                roman = word.replace(':', '')
                words[i] = word.replace(roman, self.roman_to_arabic[roman])
            # Handle word variations
            elif word.lower() in self.title_variations:
                words[i] = self.title_variations[word.lower()]

        # Rejoin words and clean up
        normalized = ' '.join(w for w in words if w)

        # Additional cleanups
        normalized = normalized.replace(' :', ':')  # Fix spacing around colons
        normalized = normalized.replace('  ', ' ')  # Fix double spaces
        normalized = normalized.strip()

        return normalized

    def get_steam_games_list(self):
        """Get complete list of Steam games"""
        cache_file = self.cache_dir / "steam_games_list.json"

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)

        print("Fetching complete Steam games list...")
        api = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
        response = requests.get(url=api)
        games_dict = {}

        for game in response.json()['applist']['apps']:
            games_dict[game['name'].lower()] = game['appid']

        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(games_dict, f)

        return games_dict

    def get_game_score(self, app_id):
        """Get game score from Steam reviews"""
        try:
            print(f"Querying Steam reviews for app_id: {app_id}")
            data = requests.get(f'https://store.steampowered.com/appreviews/{app_id}?json=1').json()
            summary = data['query_summary']
            score = summary['total_positive'] / summary['total_reviews'] if summary['total_reviews'] > 0 else None
            return score, summary['total_reviews']
        except Exception as e:
            print(f"Error getting score for {app_id}: {e}")
            return None, 0

    def get_steam_info(self, game_title):
        """Get Steam game information including platform availability"""
        # Try exact match first
        cache_file = self.cache_dir / f"{game_title.lower().replace(' ', '_')}_steam.json"

        # Check cache first with original title
        if cache_file.exists():
            print(f"Using cached data for: {game_title}")
            with open(cache_file, 'r') as f:
                return json.load(f)

        # Normalize the title
        normalized_title = self.normalize_title(game_title)
        normalized_cache_file = self.cache_dir / f"{normalized_title.lower().replace(' ', '_')}_steam.json"

        # Check cache with normalized title
        if normalized_cache_file.exists():
            print(f"Using cached data for normalized title: {normalized_title}")
            with open(normalized_cache_file, 'r') as f:
                return json.load(f)

        try:
            # Try to find game with original title
            app_id = self.steam_games.get(game_title.lower())

            # If not found, try with normalized title
            if not app_id:
                app_id = self.steam_games.get(normalized_title.lower())

            # If still not found, try fuzzy matching
            if not app_id:
                # Print debug info
                print(f"Trying to find match for: {game_title}")
                print(f"Normalized as: {normalized_title}")

                # Try matching without special characters
                clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', normalized_title.lower())
                for steam_title, steam_id in self.steam_games.items():
                    clean_steam_title = re.sub(r'[^a-zA-Z0-9\s]', '', steam_title.lower())
                    if clean_title == clean_steam_title:
                        print(f"Found fuzzy match: {steam_title}")
                        app_id = steam_id
                        break

            if not app_id:
                print(f"Could not find Steam ID for: {game_title} (normalized: {normalized_title})")
                return None

            print(f"Querying Steam store for app_id: {app_id} ({game_title})")
            # Get store API data
            store_response = requests.get(
                f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            )
            store_data = store_response.json()

            if not store_data or str(app_id) not in store_data:
                return None

            app_data = store_data[str(app_id)]
            if not app_data['success']:
                return None

            # Get user score
            user_score, total_reviews = self.get_game_score(app_id)

            # Get ProtonDB compatibility
            try:
                print(f"Querying ProtonDB for app_id: {app_id}")
                proton_response = requests.get(
                    f"https://www.protondb.com/api/v1/reports/summaries/{app_id}.json"
                )
                proton_data = proton_response.json() if proton_response.status_code == 200 else None
                proton_tier = proton_data.get('tier', 'unknown') if proton_data else 'unknown'
            except:
                proton_tier = 'unknown'

            platforms = app_data['data'].get('platforms', {})
            steam_info = {
                'app_id': app_id,
                'platforms': {
                    'windows': platforms.get('windows', False),
                    'macos': platforms.get('mac', False),
                    'linux': platforms.get('linux', False),
                    'steamdeck': proton_tier
                },
                'user_score': user_score,
                'total_reviews': total_reviews,
                'price': app_data['data'].get('price_overview', {}).get('final_formatted', 'N/A'),
                'header_image': app_data['data'].get('header_image', '')
            }

            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(steam_info, f)

            time.sleep(1)  # Rate limiting
            return steam_info

        except Exception as e:
            print(f"Error getting Steam info for {game_title}: {e}")
            return None

    def scrape_rps(self):
        print("Scraping RockPaperShotgun...")
        url = 'https://www.rockpapershotgun.com/the-rps-100-2024'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        # Find all game entries
        game_entries = soup.find_all('span', class_='top-video-game-pill')

        for entry in game_entries:
            # Find the associated game name
            name_span = entry.find_next('span', class_='top-video-game-name')
            if name_span:
                games.append({
                    'rank': int(entry.text.strip()),
                    'title': name_span.text.strip(),
                    'source': 'RPS'
                })

        return games

    def scrape_ign(self):
        print("Scraping IGN...")
        url = 'https://www.ign.com/articles/the-best-reviewed-games-of-2024'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        game_entries = soup.find_all('h3', {'class': 'title3', 'data-cy': 'title3'})

        rank = 1
        for entry in game_entries:
            original_title = entry.text.strip()
            normalized_title = self.normalize_title(original_title)

            games.append({
                'rank': rank,
                'title': normalized_title,
                'original_title': original_title,
                'source': 'IGN'
            })
            rank += 1

            # Debug output for title changes
            if original_title != normalized_title:
                print(f"Normalized title: {original_title} -> {normalized_title}")

        return games

    def scrape_pcgamer(self):
        print("Scraping PCGamer...")
        url = 'https://www.pcgamer.com/games/the-top-100-pc-games-2024/'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        games = []
        # Find all h2 tags with IDs containing game information
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

    def merge_and_deduplicate(self, all_games):
        unique_games = {}

        for game in all_games:
            title = game['title'].lower()
            if title not in unique_games:
                # Get Steam and platform info
                steam_info = self.get_steam_info(game['title'])

                game_data = {
                    'title': game['title'],
                    'rankings': {},
                    'platforms': {
                        'windows': True,
                        'macos': False,
                        'linux': False,
                        'steamdeck': 'unknown'
                    },
                    'steam_id': None,
                    'user_score': None,
                    'total_reviews': 0,
                    'price': 'N/A',
                    'header_image': ''
                }

                if steam_info:
                    game_data.update({
                        'platforms': steam_info['platforms'],
                        'steam_id': steam_info['app_id'],
                        'user_score': steam_info['user_score'],
                        'total_reviews': steam_info['total_reviews'],
                        'price': steam_info['price'],
                        'header_image': steam_info['header_image']
                    })

                unique_games[title] = game_data

            unique_games[title]['rankings'][game['source']] = game['rank']

        return list(unique_games.values())

    def run(self):
        all_games = []

        # Add delays between requests to be polite to the servers
        all_games.extend(self.scrape_rps())
        time.sleep(2)
        all_games.extend(self.scrape_ign())
        time.sleep(2)
        all_games.extend(self.scrape_pcgamer())

        # Merge and deduplicate games
        merged_games = self.merge_and_deduplicate(all_games)

        # Save raw data and merged data
        self.data_dir.mkdir(exist_ok=True)
        with open(self.data_dir / 'raw_games.json', 'w', encoding='utf-8') as f:
            json.dump(all_games, f, indent=2, ensure_ascii=False)
        with open(self.data_dir / 'merged_games.json', 'w', encoding='utf-8') as f:
            json.dump(merged_games, f, indent=2, ensure_ascii=False)

        print(f"Scraped {len(all_games)} total entries")
        print(f"Found {len(merged_games)} unique games")

        return merged_games

if __name__ == "__main__":
    scraper = GameScraper()
    scraper.run()
