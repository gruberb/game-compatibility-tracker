from game_scraper.scraper import GameScraper
from game_scraper.config import config


def main():
    # Initialize configuration first
    config.setup_config()

    # Check if RAWG API key is available
    api_key = config.get_api_key('RAWG')
    if not api_key:
        print("Please set up your RAWG API key first!")
        return

    # Create and run scraper
    scraper = GameScraper()
    games = scraper.run()
    print(f"\nScraped {len(games)} games successfully!")

    # Print some stats about the found games
    games_with_switch = sum(1 for game in games if game['platforms']['switch'])
    games_with_metacritic = sum(1 for game in games if game['metacritic'])
    print(f"\nStats:")
    print(f"- Games available on Switch: {games_with_switch}")
    print(f"- Games with Metacritic scores: {games_with_metacritic}")


if __name__ == "__main__":
    main()
