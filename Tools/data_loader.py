from .config import Config
from typing import Tuple, List, Dict, Union
import numpy as np
import os

base_path = os.path.dirname(__file__)


def load_romanization_data(file_path: str) -> Tuple[List[str], List[str], np.ndarray]:
    """

    Loads romanization data from a CSV file.

    Parameters:
    - file_path (str): The path of the CSV file containing the romanization data.

    Returns:
    - Tuple[List[str], List[str], np.ndarray]: A tuple containing the initial list, final list, and a numpy array
    representing the romanization data.

    Example Usage:
        init_list, fin_list, ar = load_romanization_data('romanization_data.csv')

    Note:
    The CSV file should be in the following format:

    Example CSV:
    ---------------------
      Romanized, a, b, c
      A, 1, 0, 1
      B, 0, 1, 0
    ---------------------

    The first row represents the final romanized letters, and the first column represents the initial letters to be
    romanized. The values in the matrix indicate whether a particular romanization is applicable (1) or not (0).

    The length of initial list should be N, and the length of final list should be M, where (N,M) is the shape of the
    matrix in the CSV file.

    """
    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    init_list = list(data[1:, 0])
    fin_list = list(data[0, 1:])
    ar = np.array(data[1:, 1:] == '1', dtype=np.bool_)
    return init_list, fin_list, ar


def load_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
    """

    Get method parameters for the given method and configuration.

    Parameters:
        method (str): The name of the method.
        config (Config): The configuration object.

    Returns:
        dict: A dictionary containing the following keys:
            - 'ar' (numpy.ndarray): The AR parameter.
            - 'init_list' (list of str): The initial list parameter.
            - 'fin_list' (list of str): The final list parameter.
            - 'method' (str): The method parameter.

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

    Load stopwords from a given file.

    Returns:
        List[str]: A list of stopwords read from the file.

    """
    file_path = os.path.join(base_path, 'data', 'stopwords.txt')
    with open(file_path, 'r') as f:
        stopwords = f.read().splitlines()
    return stopwords
