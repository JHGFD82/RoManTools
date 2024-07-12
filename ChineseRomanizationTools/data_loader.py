# data_loader.py

import numpy as np

def load_pinyin_data(file_path):
    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    init_list = list(data[1:, 0])
    fin_list = list(data[0, 1:])
    ar = data[1:, 1:] == '1'
    return init_list, fin_list, ar


def load_wadegiles_data(file_path):
    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    init_list = list(data[1:, 0])
    fin_list = list(data[0, 1:])
    ar = data[1:, 1:] == '1'
    return init_list, fin_list, ar


def load_stopwords(file_path):
    with open(file_path, 'r') as f:
        stopwords = f.read().splitlines()
    return stopwords
