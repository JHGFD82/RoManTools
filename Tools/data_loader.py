# data_loader.py
from typing import Tuple, List
import numpy as np


def load_romanization_data(file_path: str) -> Tuple[List[str], List[str], np.ndarray]:
    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    init_list = list(data[1:, 0])
    fin_list = list(data[0, 1:])
    ar = np.array(data[1:, 1:] == '1', dtype=np.bool_)
    return init_list, fin_list, ar


def load_stopwords(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        stopwords = f.read().splitlines()
    return stopwords
