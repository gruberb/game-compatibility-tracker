import json
from pathlib import Path
from typing import Dict


def load_special_cases() -> Dict[str, str]:
    special_cases_file = Path('game_scraper/special_cases.json')
    if special_cases_file.exists():
        with open(special_cases_file, 'r', encoding='utf-8') as f:
            special_cases_raw = json.load(f)
            # Lowercase all keys
            special_cases = {key.lower(): value for key, value in special_cases_raw.items()}
    else:
        special_cases = {}
    return special_cases
