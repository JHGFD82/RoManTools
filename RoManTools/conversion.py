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
    def __init__(self, convert_from: str, convert_to: str, config: Config):
        """
        Initializes the RomanizationConverter class.

        Args:
            convert_from (str): The romanization system to convert from.
            convert_to (str): The romanization system to convert to.
            config (Config): The configuration object for the conversion.
        """

        self.conversion_mapping = load_conversion_data()
        self.convert_from = convert_from
        self.convert_to = convert_to
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
            for row in self.conversion_mapping:
                if row[self.convert_from].lower() == lowercased_text:
                    if not row[self.convert_to] and row['meta'] == 'rare':
                        return text + '(!rare Pinyin!)'
                    return row[self.convert_to]
            return text + '(!)'

        if any([self.config.error_skip, self.config.error_report, self.config.crumbs]):
            # FUTURE: Add error handling for missing conversion mappings
            self.config.print_crumb(1, "Converting text", text)
            self.config.print_crumb(message='---')
        return _cached_convert(text)
