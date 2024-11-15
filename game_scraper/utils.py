import re
from typing import Optional


def clean_title_for_matching(title: str) -> str:
    """Clean title for better matching"""
    # Remove special characters and extra spaces
    clean = re.sub(r'[^\w\s]', '', title)
    # Remove non-ASCII characters
    clean = clean.encode('ascii', 'ignore').decode()
    # Remove common words that might interfere with matching
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
    clean = ' '.join(word for word in clean.lower().split()
                     if word not in stop_words)
    return clean


def is_roman_numeral(s: str) -> bool:
    """Check if a string is a Roman numeral"""
    roman_numerals = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'}
    return s.upper() in roman_numerals


def numeral_to_number(numeral: str) -> Optional[int]:
    """Convert Roman numeral or digit to integer"""
    roman_to_int = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
    }
    if numeral.isascii() and numeral.isdigit():
        return int(numeral)
    elif numeral.upper() in roman_to_int:
        return roman_to_int[numeral.upper()]
    else:
        return None
