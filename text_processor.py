import re
from syllable import Syllable
import config
from data_loader import load_csv_data, prepare_reference_data, load_conversion_map
from syllable_processor import split_syllable


def convert_romanization(text: str, method: str) -> str:
    """
    Convert given text using the provided romanization method.

    Parameters:
        text (str): The text to convert.
        method (str): Romanization method ('PYWG', 'WGPY').

    Returns:
        str: The converted text.
    """
    accepted_methods = ['PYWG', 'WGPY']
    if method not in accepted_methods:
        return text + '(!)'
    convert_dict = load_conversion_map(method)
    return convert_dict.get(text, text)


# Declaring variables for syllable_count function
pinyin_data = load_csv_data(config.PINYIN_DATA_FILE)
pinyin_init_list, pinyin_fin_list, pinyin_ar = prepare_reference_data(pinyin_data)
wadegiles_data = load_csv_data(config.WADEGILES_DATA_FILE)
wg_init_list, wg_fin_list, wg_ar = prepare_reference_data(wadegiles_data)


def syllable_count(text: str, method: str = 'PY', convert: bool = False, error_report: bool = False) -> tuple:
    """
    Produce the count of syllables from any given romanized Chinese text.

    Parameters:
        text (str): The text to analyze.
        method (str): Romanization method ('PY' for Pinyin, 'WG' for Wade-Giles).
        convert (bool): Whether to convert syllables from one romanization to another.
        error_report (bool): Whether to include error messages in the output.

    Returns:
        tuple: A tuple containing the count of valid syllables and a list of error messages (if any).
    """

    # Choose the appropriate data based on the romanization method
    if method == 'PY':
        init_list, fin_list, ar = pinyin_init_list, pinyin_fin_list, pinyin_ar
    elif method == 'WG':
        init_list, fin_list, ar = wg_init_list, wg_fin_list, wg_ar
    else:
        raise ValueError("Unsupported romanization method.")

    syllables = re.findall(r'[a-zA-ZüÜ]+', text)  # Regex to split text into syllables
    valid_syllable_count = 0
    errors = []

    for syl_text in syllables:
        # Splitting the syllable into initial and final might require a separate function or logic
        initial, final = split_syllable(syl_text)  # Assuming this function exists
        syllable = Syllable(initial, final, init_list, fin_list, ar)

        if syllable.valid:
            valid_syllable_count += 1
            if convert:
                # Convert the syllable if conversion is required
                # Assuming conversion function and logic exist
                syl_text = convert_romanization(syl_text, method)
        else:
            if error_report:
                errors.append(f"Invalid syllable: {syl_text}")

    return valid_syllable_count, errors
