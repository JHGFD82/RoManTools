"""
This module contains the RomanizationConverter class, which is used to convert romanized Chinese between different romanization systems.

Classes:
    RomanizationConverter: A class to convert romanized Chinese between different romanization systems.
"""

from functools import lru_cache
from .data_loader import load_conversion_data


class RomanizationConverter:
    """
    A class to convert romanized Chinese between different romanization systems.
    """
    def __init__(self, method_combination):
        """
        Initializes the RomanizationConverter class.

        Args:
            method_combination (str): A string specifying the conversion direction (e.g., 'py_wg' for Pinyin to
            Wade-Giles).
        """

        self.conversion_dicts = load_conversion_data(method_combination)

    @lru_cache(maxsize=10000)
    def convert(self, text: str) -> str:
        """
        Converts a given text.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """

        lowercased_text = text.lower()
        # FUTURE: Add error handling for missing conversion mappings
        return self.conversion_dicts.get(lowercased_text, text + '(!)')
