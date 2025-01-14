"""
This module contains the RomanizationConverter class, which is used to convert romanized Chinese between different romanization systems.

Classes:
    RomanizationConverter: A class to convert romanized Chinese between different romanization systems.
"""

from functools import lru_cache
from .data_loader import load_conversion_data
from .config import Config


class RomanizationConverter:
    """
    A class to convert romanized Chinese between different romanization systems.
    """
    def __init__(self, method_combination: str, config: Config):
        """
        Initializes the RomanizationConverter class.

        Args:
            method_combination (str): A string specifying the conversion direction (e.g., 'py_wg' for Pinyin to
            Wade-Giles).
        """

        self.conversion_dicts = load_conversion_data(method_combination)
        self.config = config

    def convert(self, text: str) -> str:
        """
        Converts a given text.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """

        @lru_cache(maxsize=10000)
        def _cached_convert(text_to_convert: str) -> str:
            """
            Converts a given text using an LRU cache.

            Args:
                text_to_convert (str): The text to be converted.

            Returns:
                str: The converted text based on the selected romanization conversion mappings.
            """
            lowercased_text = text_to_convert.lower()
            return self.conversion_dicts.get(lowercased_text, text_to_convert + '(!)')

        if any([self.config.error_skip, self.config.error_report, self.config.crumbs]):
            # FUTURE: Add error handling for missing conversion mappings
            self.config.print_crumb(1, "Converting text", text)
            self.config.print_crumb(message='---')
        return _cached_convert(text)
