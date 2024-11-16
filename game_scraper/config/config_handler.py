import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

class ConfigHandler:
    def __init__(self):
        self.env_prefix = 'GAME_SCRAPER_'

        # Get user's home directory for api keys
        home = Path.home()
        self.user_config_dir = home / '.config/game_scraper'
        self.user_config_file = self.user_config_dir / 'api_config.json'

        # Project config directory
        self.project_config_dir = Path(__file__).parent
        self.scrapers_config_file = self.project_config_dir / 'scrapers_config.json'

    def _load_user_config(self) -> dict:
        """Load user-specific configuration (API keys, etc.)"""
        if self.user_config_file.exists():
            with open(self.user_config_file, 'r') as f:
                return json.load(f)
        return {}

    def _load_scrapers_config(self) -> dict:
        """Load scrapers configuration"""
        if self.scrapers_config_file.exists():
            with open(self.scrapers_config_file, 'r') as f:
                return json.load(f)
        return {}

    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from environment variables first, then config file"""
        # Check environment variables first
        env_var_name = f"{self.env_prefix}{key_name}_API_KEY"
        api_key = os.getenv(env_var_name)

        # If not in environment, try config file
        if not api_key:
            config = self._load_user_config()
            api_key = config.get('api_keys', {}).get(key_name.lower())

        if not api_key:
            print(f"""
API key not found! Please either:
1. Set environment variable {env_var_name}
   OR
2. Create a config file at {self.user_config_file} with content:
   {{
       "api_keys": {{
           "{key_name.lower()}": "your-api-key-here"
       }}
   }}
""")

        return api_key

    def get_scraper_config(self) -> Dict[str, Any]:
        """Get scraper configuration"""
        return self._load_scrapers_config()

    def setup_config(self):
        """Create config directories and sample files if they don't exist"""
        # Create user config directory and file
        self.user_config_dir.mkdir(exist_ok=True)

        if not self.user_config_file.exists():
            sample_user_config = {
                "api_keys": {
                    "rawg": "your_rawg_api_key_here"
                }
            }

            with open(self.user_config_file, 'w') as f:
                json.dump(sample_user_config, f, indent=2)

            print(f"""
Created sample API config file at {self.user_config_file}
Please update it with your actual API keys using the following format:
{json.dumps(sample_user_config, indent=2)}
""")

    def update_scraper_config(self, new_scraper_config: Dict[str, Any]):
        """Update scrapers configuration file"""
        with open(self.scrapers_config_file, 'w') as f:
            json.dump(new_scraper_config, f, indent=2)
