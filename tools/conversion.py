import os
import csv


class RomanizationConverter:
    """
    A class to convert romanized Chinese between different romanization systems.
    """
    def __init__(self, method_combination):
        """
        Initializes the RomanizationConverter.

        Args:
            method_combination (str): A string specifying the conversion direction (e.g., 'py_wg' for Pinyin to
            Wade-Giles).
        """
        self.conversion_dicts = {}
        self.load_conversion_data(method_combination)

    def load_conversion_data(self, method_combination: str):
        """
        Loads the conversion mappings based on the method combination specified during initialization.

        Args:
            method_combination (str): A string specifying the conversion direction (e.g., 'py_wg' for Pinyin to
            Wade-Giles).
        """
        base_path = os.path.dirname(__file__)
        accepted_methods = ['py_wg', 'wg_py']
        if method_combination in accepted_methods:
            source_file = os.path.join(base_path, 'data', f'{method_combination}.csv')
            with open(source_file) as file:
                r = csv.reader(file)
                self.conversion_dicts = {rows[0]: rows[1] for rows in r}
        else:
            raise ValueError(f'Method {method_combination} not supported.')

    def convert(self, text: str) -> str:
        """
        Converts a given text.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """
        return self.conversion_dicts.get(text, text + '(!)')
