import numpy as np
import csv
from typing import Tuple, List
from config import (PINYIN_DATA_FILE, WADEGILES_DATA_FILE, STOPWORDS_FILE, PINYIN_WADEGILES_CONVERSION_FILE,
                    WADEGILES_PINYIN_CONVERSION_FILE)


def load_csv_data(file_path: str) -> np.ndarray:
    """
    Load data from a CSV file into a Numpy array.

    Parameters:
        file_path (str): The path to the CSV file.

    Returns:
        np.ndarray: Data loaded from the CSV file.
    """
    try:
        return np.genfromtxt(file_path, delimiter=',', dtype=str)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


def prepare_reference_data(csv_data: np.ndarray) -> Tuple[List[str], List[str], np.ndarray | bool]:
    """
    Prepare reference data from a CSV file.

    Parameters:
        csv_data (np.ndarray): The raw data loaded from the CSV file.

    Returns:
        Tuple[List[str], List[str], np.ndarray]:
        - A list of initials.
        - A list of finals.
        - A Numpy array for further processing.
    """
    init_list = list(csv_data[1:, 0])
    fin_list = list(csv_data[0, 1:])
    array = csv_data[1:, 1:] == '1'
    return init_list, fin_list, array


def load_conversion_map(conversion_type: str) -> dict:
    """
    Loads a conversion map from a specified CSV file.

    Parameters:
        conversion_type (str): The type of conversion map to load (e.g., 'PYWG' or 'WGPY').

    Returns:
        dict: A dictionary with the conversion map.
    """
    file_paths = {
        'PYWG': PINYIN_WADEGILES_CONVERSION_FILE,
        'WGPY': WADEGILES_PINYIN_CONVERSION_FILE
    }

    file_path = file_paths.get(conversion_type)
    if not file_path:
        raise ValueError(f"Invalid conversion type: {conversion_type}")

    conversion_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                source_syllable, target_syllable = row
                conversion_map[source_syllable] = target_syllable
    return conversion_map


def load_stopwords(file_path: str) -> List[str]:
    """
    Load stopwords from a text file.

    Parameters:
        file_path (str): The path to the text file containing stopwords.

    Returns:
        List[str]: A list of stopwords.
    """
    try:
        with open(file_path, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


# Example usage
if __name__ == "__main__":
    # Load Pinyin data
    pinyin_data = load_csv_data(PINYIN_DATA_FILE)
    pinyin_init_list, pinyin_fin_list, pinyin_array = prepare_reference_data(pinyin_data)

    # Load Wade-Giles data
    wadegiles_data = load_csv_data(WADEGILES_DATA_FILE)
    wg_init_list, wg_fin_list, wg_array = prepare_reference_data(wadegiles_data)

    # Load stopwords
    stopwords = load_stopwords(STOPWORDS_FILE)

    # Example print statements for testing
    print(f"Pinyin initials: {pinyin_init_list[:5]}")
    print(f"Wade-Giles finals: {wg_fin_list[:5]}")
    print(f"First 5 stopwords: {stopwords[:5]}")
