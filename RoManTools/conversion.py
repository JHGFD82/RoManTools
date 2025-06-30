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
        self._cached_convert = self._make_cached_convert()

    def _make_cached_convert(self):
        """
        Creates a cached conversion function bound to the current instance's mapping and settings.

        Returns:
            Callable[[str], str]: A function that converts text using an LRU cache.
        """
        conversion_mapping = self.conversion_mapping
        convert_from = self.convert_from
        convert_to = self.convert_to

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
            for row in conversion_mapping:
                if row[convert_from].lower() == lowercased_text:
                    if not row[convert_to] and row['meta'] == 'rare':
                        return text_to_convert + '(!rare Pinyin!)'
                    return row[convert_to]
            return text_to_convert + '(!)'
        return _cached_convert

    def convert(self, text: str) -> str:
        """
        Converts a given text and prints a crumb if enabled in the config.
        Also prints a crumb if the result was loaded from the cache.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """
        cache = self._cached_convert.cache_info()
        before_hits = cache.hits
        result = self._cached_convert(text)
        after_hits = self._cached_convert.cache_info().hits

        if after_hits > before_hits and self.config.crumbs:
            self.config.print_crumb(2, "Cached", f'"{text}" -> "{result}"')
        else:
            self.config.print_crumb(2, "Converted text", f'"{text}" -> "{result}"')
        return result
