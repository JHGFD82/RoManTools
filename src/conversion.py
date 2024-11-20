from functools import lru_cache
from data_loader import load_conversion_data


class RomanizationConverter:
    """
    A class to convert romanized Chinese between different romanization systems.
    """
    def __init__(self, method_combination):
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
        return self.conversion_dicts.get(lowercased_text, text + '(!)')
