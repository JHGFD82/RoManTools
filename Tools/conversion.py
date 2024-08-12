import os
import csv


class RomanizationConverter:
    def __init__(self, method):
        self.conversion_dicts = {}
        self.load_conversion_data(method)

    def load_conversion_data(self, method: str):
        base_path = os.path.dirname(__file__)
        accepted_methods = ['py_wg', 'wg_py']
        if method in accepted_methods:
            source_file = os.path.join(base_path, 'data', f'{method}.csv')
            with open(source_file) as file:
                r = csv.reader(file)
                self.conversion_dicts = {rows[0]: rows[1] for rows in r}
        else:
            raise ValueError(f'Method {method} not supported.')

    def convert(self, text: str) -> str:
        """
        Converts text from one romanization method to another.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text, if the method is valid. Otherwise, the original text with '(!)' appended.
        """

        return self.conversion_dicts.get(text, text + '(!)')
