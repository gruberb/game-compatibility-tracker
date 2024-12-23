import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher
import requests

from .config import config
from .special_cases import load_special_cases
from .utils import (
    clean_title_for_matching,
    is_roman_numeral,
    numeral_to_number,
)
from .scrapers import get_all_scrapers

class GameScraper:
    def __init__(self):
        # Initialize config handler
        config.setup_config()
        self.rawg_api_key = config.get_api_key('RAWG')
        if not self.rawg_api_key:
            raise ValueError("RAWG API key not found in environment variables or config file")

        self.headers: Dict[str, str] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_dir: Path = Path('docs/data')
        self.cache_dir: Path = Path('cache')
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.FUZZY_MATCH_THRESHOLD: float = 0.90

        # Load special cases
        self.special_cases: Dict[str, str] = load_special_cases()

        # Load Steam games list
        self.steam_games: Dict[str, int] = self.get_steam_games_list()

        # Collect all games which couldn't be found
        self.unmatched_games: List[str] = []

        # Load all scrapers - they're already instantiated
        self.scrapers: List[BaseScraper] = get_all_scrapers()

    def normalize_title(self, title: str) -> str:
        """Normalize game title to improve matching"""
        # Remove trademark symbols
        title = title.replace('®', '').replace('™', '')

        # Remove years in parentheses but keep other content
        title = re.sub(r'\s*\((\d{4})\)', '', title)

        # Remove extra spaces and special characters at the ends
        title = title.strip().strip(':').strip('-')

        # Lowercase the title for consistent matching
        lower_title = title.lower()

        # Check special cases (case-insensitive)
        if lower_title in self.special_cases:
            return self.special_cases[lower_title]

        # Replace Arabic numerals with Roman numerals up to 10
        arabic_to_roman = {
            '1': 'I',
            '2': 'II',
            '3': 'III',
            '4': 'IV',
            '5': 'V',
            '6': 'VI',
            '7': 'VII',
            '8': 'VIII',
            '9': 'IX',
            '10': 'X'
        }

        words = title.split()
        for i, word in enumerate(words):
            # Replace Arabic numerals with Roman numerals if appropriate
            if word in arabic_to_roman:
                # Do not replace in certain titles
                exceptions = ['titanfall', 'mass effect', 'battlefield', 'call of duty']
                if not any(exception in lower_title for exception in exceptions):
                    words[i] = arabic_to_roman[word]
            else:
                # Remove colons and extra spaces
                words[i] = word.strip(':').strip()

        normalized_title = ' '.join(words)
        return normalized_title

    def get_rawg_info(self, game_title: str) -> Optional[Dict[str, Any]]:
        """Get game information from RAWG API"""
        cache_file = self.cache_dir / f"{game_title.lower().replace(' ', '_')}_rawg.json"

        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        try:
            url = "https://api.rawg.io/api/games"
            params = {
                "key": self.rawg_api_key,
                "search": game_title,
                "page_size": 1
            }

            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"RAWG API error: Status {response.status_code}")
                return None

            data = response.json()
            if not data['results']:
                print(f"No RAWG data found for: {game_title}")
                return None

            game = data['results'][0]

            # Extract platforms and stores
            platforms = [platform['platform']['name'] for platform in game['platforms']]
            stores = [store['store']['name'] for store in game.get('stores', [])]

            rawg_info = {
                'name': game['name'],
                'background_image': game['background_image'],
                'platforms': platforms,
                'stores': stores,
                'rating': game.get('rating'),
                'metacritic': game.get('metacritic'),
                'released': game.get('released')
            }

            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(rawg_info, f, indent=2)

            time.sleep(1)  # Rate limiting
            return rawg_info

        except Exception as e:
            print(f"Error getting RAWG info for {game_title}: {e}")
            return None

    def get_steam_games_list(self) -> Dict[str, int]:
        """Get complete list of Steam games"""
        cache_file = self.cache_dir / "steam_games_list.json"

        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        print("Fetching complete Steam games list...")
        api = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
        response = requests.get(url=api)
        games_dict: Dict[str, int] = {}  # Initialize games_dict here

        for game in response.json()['applist']['apps']:
            # Normalize the game name
            normalized_name = self.normalize_title(game['name'])
            games_dict[normalized_name.lower()] = game['appid']

        # Cache the results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(games_dict, f)

        return games_dict

    def title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity ratio between two titles, considering numeral mismatches"""
        clean1 = clean_title_for_matching(title1)
        clean2 = clean_title_for_matching(title2)

        # Split into words
        words1 = clean1.split()
        words2 = clean2.split()

        # Extract numerals from titles and convert to integers
        numerals1 = [numeral_to_number(w) for w in words1 if (w.isascii() and w.isdigit()) or is_roman_numeral(w)]
        numerals2 = [numeral_to_number(w) for w in words2 if (w.isascii() and w.isdigit()) or is_roman_numeral(w)]

        # If numerals are present and do not match, return low similarity
        if numerals1 and numerals2 and numerals1 != numerals2:
            return 0.0

        # Compute similarity
        ratio = SequenceMatcher(None, clean1, clean2).ratio()
        return ratio

    def get_game_score(self, app_id: int) -> (Optional[float], int):
        """Get game score from Steam reviews"""
        try:
            print(f"Querying Steam reviews for app_id: {app_id}")
            data = requests.get(f'https://store.steampowered.com/appreviews/{app_id}?json=1').json()
            summary = data.get('query_summary', {})
            total_reviews = summary.get('total_reviews', 0)
            total_positive = summary.get('total_positive', 0)
            score = total_positive / total_reviews if total_reviews > 0 else None
            return score, total_reviews
        except Exception as e:
            print(f"Error getting score for {app_id}: {e}")
            return None, 0

    def find_best_match(self, title: str, steam_titles: List[str]) -> Optional[str]:
        """Find the best matching Steam title"""
        best_ratio = 0.0
        best_match = None

        for steam_title in steam_titles:
            ratio = self.title_similarity(title, steam_title)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = steam_title

        return best_match if best_ratio >= self.FUZZY_MATCH_THRESHOLD else None

    def get_steam_info(self, game_title: str) -> Optional[Dict[str, Any]]:
        """Get Steam game information including platform availability"""
        cache_file = self.cache_dir / f"{game_title.lower().replace(' ', '_')}_steam.json"

        # Check cache first with original title
        if cache_file.exists():
            print(f"Using cached data for: {game_title}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Normalize the title
        normalized_title = self.normalize_title(game_title)
        normalized_cache_file = self.cache_dir / f"{normalized_title.lower().replace(' ', '_')}_steam.json"

        # Check cache with normalized title
        if normalized_cache_file.exists():
            print(f"Using cached data for normalized title: {normalized_title}")
            with open(normalized_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        try:
            print(f"\nTrying to find Steam match for: {game_title}")
            print(f"Normalized as: {normalized_title}")

            # Try exact matches first
            app_id = self.steam_games.get(game_title.lower()) or \
                     self.steam_games.get(normalized_title.lower())

            # If no exact match, try fuzzy matching
            if not app_id:
                print(f"Trying fuzzy match...")
                best_match = self.find_best_match(normalized_title, list(self.steam_games.keys()))

                if best_match:
                    similarity = self.title_similarity(normalized_title, best_match)
                    print(f"Found fuzzy match: {best_match} (similarity: {similarity:.2f})")
                    app_id = self.steam_games[best_match]
                else:
                    print(f"No good matches found for: {game_title}")
                    self.unmatched_games.append(game_title)
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
                    'steamdeck': proton_tier,
                    'switch': False  # Default value for Switch
                },
                'stores': ['Steam'],  # Initialize with Steam store
                'user_score': user_score,
                'total_reviews': total_reviews,
                'price': app_data['data'].get('price_overview', {}).get('final_formatted', 'N/A'),
                'header_image': app_data['data'].get('header_image', '')
            }

            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(steam_info, f)

            time.sleep(1)  # Rate limiting
            return steam_info

        except Exception as e:
            print(f"Error getting Steam info for {game_title}: {e}")
            return None

    def merge_and_deduplicate(self, all_games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique_games: Dict[str, Dict[str, Any]] = {}

        for game in all_games:
            normalized_title = self.normalize_title(game['title'])
            title_key = normalized_title.lower()

            if title_key not in unique_games:
                # Get Steam and platform info
                steam_info = self.get_steam_info(normalized_title)
                # Get RAWG info
                rawg_info = self.get_rawg_info(normalized_title)

                game_data = {
                    'title': normalized_title,
                    'rankings': {},
                    'platforms': {
                        'windows': True,
                        'macos': False,
                        'linux': False,
                        'steamdeck': 'unknown',
                        'switch': False
                    },
                    'stores': [],
                    'steam_id': None,
                    'user_score': None,
                    'total_reviews': 0,
                    'price': 'N/A',
                    'header_image': '',
                    'metacritic': None,
                    'release_date': None
                }

                if steam_info:
                    game_data.update({
                        'platforms': steam_info.get('platforms', game_data['platforms']),
                        'steam_id': steam_info.get('app_id'),
                        'user_score': steam_info.get('user_score'),
                        'total_reviews': steam_info.get('total_reviews', 0),
                        'price': steam_info.get('price', 'N/A'),
                    })
                    # Add Steam to stores if it's not already there
                    if 'Steam' not in game_data['stores']:
                        game_data['stores'].append('Steam')

                print(f"{rawg_info}")
                if rawg_info:
                    # Update platforms with Switch availability
                    if 'Nintendo Switch' in rawg_info.get('platforms', []):
                        game_data['platforms']['switch'] = True
                    # Update stores
                    game_data['stores'].extend([
                        store for store in rawg_info.get('stores', [])
                        if store not in game_data['stores']
                    ])
                    # Use RAWG image if we don't have one from Steam
                    if not game_data['header_image'] and rawg_info.get('background_image'):
                        game_data['header_image'] = rawg_info['background_image']
                    # Add additional RAWG data
                    game_data['metacritic'] = rawg_info.get('metacritic')
                    game_data['release_date'] = rawg_info.get('released')

                unique_games[title_key] = game_data

            unique_games[title_key]['rankings'][game['source']] = game['rank']

        return list(unique_games.values())

    def run(self) -> List[Dict[str, Any]]:
        all_games = []

        for scraper in self.scrapers:
            print(f"Scraping {scraper.name}...")
            games = scraper.scrape(self.headers)
            all_games.extend(games)
            time.sleep(2)  # Politeness delay

        # Merge and deduplicate games
        merged_games = self.merge_and_deduplicate(all_games)

        # Save raw data and merged data
        self.data_dir.mkdir(exist_ok=True)
        with open(self.data_dir / 'raw_games.json', 'w', encoding='utf-8') as f:
            json.dump(all_games, f, indent=2, ensure_ascii=False)
        with open(self.data_dir / 'merged_games.json', 'w', encoding='utf-8') as f:
            json.dump(merged_games, f, indent=2, ensure_ascii=False)

        # Write unmatched games to a file
        if self.unmatched_games:
            unmatched_file = self.data_dir / 'unmatched_games.txt'
            with open(unmatched_file, 'w', encoding='utf-8') as f:
                for game in self.unmatched_games:
                    f.write(game + '\n')
            print(f"Unmatched games written to {unmatched_file}")

        print(f"Scraped {len(all_games)} total entries")
        print(f"Found {len(merged_games)} unique games")

        return merged_games
