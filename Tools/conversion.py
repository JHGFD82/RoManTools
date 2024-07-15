import os
import csv


class RomanizationConverter:
    def __init__(self):
        self.conversion_dicts = {}
        self.load_conversion_data()

    def load_conversion_data(self):
        base_path = os.path.dirname(__file__)
        accepted_methods = ['PYWG', 'WGPY']
        for method in accepted_methods:
            source_file = os.path.join(base_path, 'data', f'{method}.csv')
            with open(source_file) as file:
                r = csv.reader(file)
                self.conversion_dicts[method] = {rows[0]: rows[1] for rows in r}

    def convert(self, text: str, method: str) -> str:
        """
        Converts text from one romanization method to another.

        Args:
            text (str): The text to be converted.
            method (str): The romanization method to convert to. Accepted methods are 'PYWG' and 'WGPY'.

        Returns:
            str: The converted text, if the method is valid. Otherwise, the original text with '(!)' appended.
        """
        if method not in self.conversion_dicts:
            return text + '(!)'

        return self.conversion_dicts[method].get(text, text + '(!)')
