# data_loader.py
from typing import Tuple, List
import numpy as np


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


def load_stopwords(file_path: str) -> List[str]:
    """

    Load stopwords from a given file.

    Parameters:
        file_path (str): The path to the file containing the stopwords.

    Returns:
        List[str]: A list of stopwords read from the file.

    """
    with open(file_path, 'r') as f:
        stopwords = f.read().splitlines()
    return stopwords
