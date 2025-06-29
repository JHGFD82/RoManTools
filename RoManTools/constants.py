"""
Constants for romanized Mandarin text processing.

This module provides various constants used throughout the text processing system, including:
- Vowels set for identifying vowel characters.
- Apostrophes set for identifying apostrophe characters.
- Dashes set for identifying dash characters.
- Supported contractions set for identifying valid contractions.

Constants:
    vowels (Set[str]): A set of vowel characters used in romanized Mandarin text.
    apostrophes (Set[str]): A set of apostrophe characters used in romanized Mandarin text.
    dashes (Set[str]): A set of dash characters used in romanized Mandarin text.
    supported_contractions (Set[str]): A set of valid contractions used in romanized Mandarin text.
"""

from typing import Dict, Tuple, Any

vowels = {'a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ'}
apostrophes = {"'", "’", "‘", "ʼ", "ʻ", "`"}
dashes = {"-", "–", "—"}
supported_contractions = {"s", "d", "ll"}
supported_methods = {
    'pinyin': {'shorthand': 'py', 'pretty': 'Pinyin'},
    'wade-giles': {'shorthand': 'wg', 'pretty': 'Wade-Giles'}
}
supported_actions = {
    'convert': {'pretty': 'Convert Text'},
    'cherry_pick': {'pretty': 'Cherry Pick'},
    'segment': {'pretty': 'Segmentation'},
    'validator': {'pretty': 'Validator'},
    'syllable_count': {'pretty': 'Syllable Count'},
    'detect_method': {'pretty': 'Detect Method'}
}
supported_config = {
    'crumbs': {'pretty': 'Print Crumbs'},
    'error_skip': {'pretty': 'Skip Errors'},
    'error_report': {'pretty': 'Report Errors'}
}
nontext_chars = {
    ' ': {'pretty': '[space]'},
    '\n': {'pretty': '[newline]'},
    '\t': {'pretty': '[tab]'},
    '\r': {'pretty': '[carriage_return]'},
    '\f': {'pretty': '[form_feed]'},
    '\v': {'pretty': '[vertical_tab]'}
}

def alias_maps(support_dict: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Given a dictionary with 'shorthand' keys, returns (shorthand_to_full, full_to_shorthand) mappings.
    """
    shorthand_to_full: Dict[str, str] = {v['shorthand']: k for k, v in support_dict.items()}
    full_to_shorthand: Dict[str, str] = {k: v['shorthand'] for k, v in support_dict.items()}
    return shorthand_to_full, full_to_shorthand

method_shorthand_to_full, method_full_to_shorthand = alias_maps(supported_methods)
