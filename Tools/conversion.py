# conversion.py

import csv
import os


def convert_romanization(text, method):
    accepted_methods = ['PYWG', 'WGPY']

    if method not in accepted_methods:
        return text + '(!)'

    base_path = os.path.dirname(__file__)
    source_file = os.path.join(base_path, 'data', f'{method}.csv')

    with open(source_file) as file:
        r = csv.reader(file)
        convert_dict = {rows[0]: rows[1] for rows in r}
    converted = convert_dict[text]

    return converted
