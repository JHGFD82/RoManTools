from .config import Config
from typing import Tuple, List, Dict, Union
import numpy as np
import os

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


def load_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
    """
    Loads romanization method parameters including initials, finals, and the valid combinations array.

    Args:
        method (str): The romanization method (e.g., 'py', 'wg').
        config (Config): Configuration object containing settings like crumbs, error_skip, and error_report.

    Returns:
        Dict[str, List[str], np.ndarray]: A dictionary containing initials, finals, and the valid combinations array.
    """
    method_file = f'{method}DF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method_file}.csv'))

    if config.crumbs:
        print(f"# {method.upper()} romanization data loaded #")

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
    with open(file_path, 'r') as f:
        stopwords = f.read().splitlines()
    return stopwords
