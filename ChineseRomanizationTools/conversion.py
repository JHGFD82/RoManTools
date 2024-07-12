# conversion.py

import csv

def convert_romanization(text, method):
    accepted_methods = ['PYWG', 'WGPY']

    if method not in accepted_methods:
        return text + '(!)'

    source_file = 'data/' + f'{method}.csv'

    with open(source_file) as file:
        r = csv.reader(file)
        convert_dict = {rows[0]: rows[1] for rows in r}
    converted = convert_dict[text]

    return converted
