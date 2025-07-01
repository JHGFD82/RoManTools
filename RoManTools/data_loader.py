"""
Data loading utilities for romanized Mandarin text processing.

This module provides functions to load various data required for processing romanized Mandarin text, including:
- Romanization data (initials, finals, and valid combinations).
- Conversion mappings between different romanization methods.
- Method parameters for specific romanization methods.
- Stopwords list.

Functions:
    load_romanization_data(file_path: str) -> Tuple[List[str], List[str], Tuple[Tuple[bool, ...], ...]]:
        Load romanization data from a CSV file and return initials, finals, and a 2D array indicating valid combinations.
    load_conversion_data() -> List[Dict[str, str]]:
        Load the conversion mappings between different romanization methods.
    load_method_params(method: str) -> Dict[str, Union[Tuple[Tuple[bool, ...], ...], List[str], str]]:
        Load romanization method parameters including initials, finals, and the valid combinations array.
    load_stopwords() -> List[str]:
        Load a list of stopwords from a text file.

Usage Example:
    >>> initials, finals, ar = load_romanization_data('data/pyDF.csv')
    >>> mappings = load_conversion_data()
    >>> params = load_method_params('py')
    >>> stopwords = load_stopwords()
"""

from typing import Tuple, List, Dict, Union
import os
import csv


base_path = os.path.dirname(__file__)


def load_romanization_data(file_path: str) -> Tuple[List[str], List[str], Tuple[Tuple[bool, ...], ...]]:
    """
    Loads romanization data from a CSV file and returns the initials, finals, and a nested tuple indicating valid
    combinations.

    Args:
        file_path (str): The path to the CSV file containing romanization data.

    Returns:
        Tuple[List[str], List[str], Tuple[Tuple[bool, ...], ...]]]: A tuple containing the following:
            - List of initials.
            - List of finals.
            - A nested tuple representing valid initial-final combinations.
    """

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
    init_list = [row[0] for row in data[1:]]
    fin_list = data[0][1:]
    ar = tuple(tuple(cell == '1' for cell in row[1:]) for row in data[1:])
    return init_list, fin_list, ar


def load_conversion_data() -> List[Dict[str, str]]:
    """
    Loads the conversion mappings based on the method combination specified during initialization.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing conversion mappings between different romanization methods.
    """

    source_file = os.path.join(base_path, 'data', 'conversion_mapping.csv')
    mappings: List[Dict[str, str]] = []
    with open(source_file, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            mappings.append(row)
    return mappings


def load_method_params(method: str) -> Dict[str, Union[Tuple[Tuple[bool, ...], ...], List[str], str]]:
    """
    Loads romanization method parameters including initials, finals, and the valid combinations array.

    Args:
        method (str): The romanization method (e.g., 'py', 'wg').

    Returns:
        Dict[str, List[str], np.ndarray]: A dictionary containing initials, finals, and the valid combinations array.
    """

    method_file = f'{method}DF'
    try:
        init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method_file}.csv'))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Syllable array for method '{method}' not found.") from exc
    return {
        'ar': ar,
        'init_list': init_list,
        'fin_list': fin_list,
        'method': method
    }


def load_stopwords() -> List[str]:
    """
    Loads a list of stopwords from a text file.

    Returns:
        List[str]: A list of stopwords.
    """

    file_path = os.path.join(base_path, 'data', 'stopwords.txt')
    with open(file_path, encoding='utf-8') as f:
        stopwords = f.read().splitlines()
    return stopwords
