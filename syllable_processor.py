from syllable import Syllable

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']  # Vowel list


def find_initial(text: str, init_list: list) -> dict:
    """
    Identify the initial of the syllable.

    Parameters:
        text (str): The text to analyze for initial.
        init_list (list): The list of valid initials.

    Returns:
        dict: Dictionary with initial and possible error message.
    """
    initial = ''
    result = {}

    for i, c in enumerate(text):
        if c in vowel:
            if i == 0:  # a syllable starts with a vowel
                result.update({'initial': 'ø'})
            else:
                initial = text[:i]
                if initial not in init_list:  # an invalid initial
                    result.update({'initial': initial, 'error': f'{initial}: invalid initial'})
                else:
                    result.update({'initial': initial})
            return result

    if not initial:
        result.update({'initial': text, 'error': f'{text}: no final'})
        return result


def find_final(text: str, fin_list: list) -> str:
    """
    Identify the final part of the syllable, handling special cases and exceptions.

    Parameters:
        text (str): The text to analyze for the final part.
        fin_list (list): The list of valid finals.
        syllable_validator (function): Function to validate a syllable.

    Returns:
        str: The final part of the syllable.
    """
    final = ''

    for i, c in enumerate(text):
        if c in vowel:
            if i + 1 == len(text):  # Ending vowel
                final = text
                break

            # Check for valid multi-vowel combinations
            elif i > 0:
                test_finals = [f_item for f_item in fin_list if f_item.startswith(text[:i + 1])]
                if not any(Syllable.validate_syllable(text[:i + 1], f_item) for f_item in test_finals):
                    final = text[:i]
                    break

        else:  # Consonant
            remainder = len(text) - i - 1

            # Handle 'er', 'erh'
            if text[i - 1:i + 1] == 'er' and (not remainder or text[i + 1] not in vowel):
                final = text[:-2] if len(text[:i]) > 1 else text[:i - 1]

            # Handle 'n', 'ng'
            elif c == 'n':
                if remainder and text[i + 1] == 'g' and not (text, text[:i + 2]):
                    final = text[:i + 2]
                else:
                    final = text[:i + 1] if not remainder or text[i + 1] not in vowel else text[:i]

            else:  # Other consonants
                final = text[:i]

            break

    return final


def split_syllable(text: str, init_list: list, fin_list: list) -> tuple:
    """
    Splits a given syllable into its initial and final parts using find_initial and find_final.

    Parameters:
        text (str): The syllable to split.
        init_list (list): List of valid initials.
        fin_list (list): List of valid finals.

    Returns:
        tuple: The initial and final parts of the syllable.
    """
    initial_result = find_initial(text, init_list=init_list)
    final_result = find_final(text, fin_list=fin_list)

    initial = initial_result.get('initial', '')
    final = final_result.get('final', '')

    return initial, final
