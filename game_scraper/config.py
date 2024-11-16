import os
from pathlib import Path
from typing import Optional
import json

class ConfigHandler:
    def __init__(self):
        # Get user's home directory
        home = Path.home()

        # Create .game_scraper directory in user's home
        self.config_dir = home / '.config/game_scraper'
        self.config_file = self.config_dir / 'config.json'
        self.env_prefix = 'GAME_SCRAPER_'

    def _load_config_file(self) -> dict:
        """Load configuration from JSON file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def get_api_key(self, key_name: str) -> Optional[str]:
        """
        Get API key from environment variables first, then config file

        Args:
            key_name: Name of the API key (e.g., 'RAWG')
        """
        # Check environment variables first
        env_var_name = f"{self.env_prefix}{key_name}_API_KEY"
        api_key = os.getenv(env_var_name)

        # If not in environment, try config file
        if not api_key:
            config = self._load_config_file()
            api_key = config.get('api_keys', {}).get(key_name.lower())

        if not api_key:
            print(f"""
API key not found! Please either:
1. Set environment variable {env_var_name}
   OR
2. Create a config file at {self.config_file} with content:
   {{
       "api_keys": {{
           "rawg": "your-api-key-here"
       }}
   }}
""")

        return api_key

    def setup_config(self):
        """Create config directory and sample config file if they don't exist"""
        # Create config directory
        self.config_dir.mkdir(exist_ok=True)

        # Create sample config if it doesn't exist
        if not self.config_file.exists():
            sample_config = {
                "api_keys": {
                    "rawg": "your_rawg_api_key_here"
                }
            }

            with open(self.config_file, 'w') as f:
                json.dump(sample_config, f, indent=2)

            print(f"""
Created sample config file at {self.config_file}
Please update it with your actual API keys using the following format:
{{
    "api_keys": {{
        "rawg": "your-actual-api-key-here"
    }}
}}
""")
