"""
Data loading utilities for romanized Mandarin text processing.

This module provides functions to load various data required for processing romanized Mandarin text,
including:
- Romanization data (initials, finals, and valid combinations).
- Conversion mappings between different romanization methods.
- Method parameters for specific romanization methods.
- Stopwords list.
- Syllable list.

Functions:
    load_romanization_data(file_path: str) -> Tuple[List[str], List[str], np.ndarray]:
        Loads romanization data from a CSV file and returns initials, finals, and a 2D array indicating valid combinations.

    load_conversion_data(method_combination: str) -> Dict[str, str]:
        Loads the conversion mappings based on the specified method combination.

    load_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
        Loads romanization method parameters including initials, finals, and the valid combinations array.

    load_stopwords() -> List[str]:
        Loads a list of stopwords from a text file.
"""

from typing import Tuple, List, Dict, Union
import os
import csv
import numpy as np


base_path = os.path.dirname(__file__)


def load_romanization_data(file_path: str) -> Tuple[List[str], List[str], np.ndarray]:
    """
    Loads romanization data from a CSV file and returns the initials, finals, and a 2D array indicating valid
    combinations.

    Args:
        file_path (str): The path to the CSV file containing romanization data.

    Returns:
        Tuple[List[str], List[str], np.ndarray]: A tuple containing the following:
            - List of initials.
            - List of finals.
            - A 2D numpy array representing valid initial-final combinations.
    """

    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    init_list = list(data[1:, 0])
    fin_list = list(data[0, 1:])
    ar = np.array(data[1:, 1:] == '1', dtype=np.bool_)
    return init_list, fin_list, ar


def load_conversion_data(method_combination: str):
    """
    Loads the conversion mappings based on the method combination specified during initialization.

    Args:
        method_combination (str): A string specifying the conversion direction (e.g., 'py_wg' for Pinyin to
        Wade-Giles).
    """

    accepted_methods = ['py_wg', 'wg_py']
    if method_combination in accepted_methods:
        source_file = os.path.join(base_path, 'data', f'{method_combination}.csv')
        with open(source_file, encoding='utf-8') as file:
            r = csv.reader(file)
            return {rows[0]: rows[1] for rows in r}
    else:
        raise ValueError(f'Method {method_combination} not supported.')


def load_method_params(method: str) -> Dict[str, Union[List[str], np.ndarray]]:
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
    # if config.crumbs:
    #     print(f"# {method.upper()} romanization data loaded #")
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
