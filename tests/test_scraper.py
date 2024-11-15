import unittest
from game_scraper.scrapers.ign_scraper import IGNScraper

class TestIGNScraper(unittest.TestCase):
    def test_scrape(self):
        scraper = IGNScraper()
        headers = {'User-Agent': 'Mozilla/5.0'}
        games = scraper.scrape(headers)
        self.assertIsInstance(games, list)
        self.assertGreater(len(games), 0)
        for game in games:
            self.assertIn('rank', game)
            self.assertIn('title', game)
            self.assertIn('source', game)

if __name__ == '__main__':
    unittest.main()
