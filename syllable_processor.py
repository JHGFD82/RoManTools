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


def find_final(text: str, fin_list: list) -> dict:
    """
    Identify the final of the syllable.

    Parameters:
        text (str): The text to analyze for final.
        fin_list (list): The list of valid finals.

    Returns:
        dict: Dictionary with final and possible error message.
    """
    result = {}
    vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']  # Vowel list

    for i, c in enumerate(text):
        if c in vowel and i + 1 == len(text):
            result.update({'final': text})
            return result
        elif c in vowel and i > 0:
            test_finals = [f_item for f_item in fin_list if f_item.startswith(text[:i + 1])]
            if not any(test_finals):
                result.update({'final': text[:i], 'error': f'{text[:i]}: invalid final'})
                return result
        elif c not in vowel:

            # EXCEPTIONS #
            # reference variable to identify end of text
            remainder = len(text) - i - 1

            # er, erh #
            # if syllable before "er", return it, else return "er"
            if (text[i - 1:i + 1] == 'er' and
                    (not remainder or text[i + 1] not in vowel)):
                final = text[:-2] if len(text[:i]) > 1 else text[:i - 1]

            # n, ng #
            elif c == 'n':
                # if there's potential text for final or an invalid "n" final, return "ng", else return "n"
                if remainder and text[i + 1] == 'g':
                    kwargs.update({'final': text[:i + 1]})
                    final = text[:i + 2] if (remainder < 2 or text[i + 2] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i + 1]

                # if there's potential text for final or an invalid final without "n", return "n"
                else:
                    kwargs.update({'final': text[:i]})
                    final = text[:i + 1] if (not remainder or text[i + 1] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i]

            # stop at all other consonants
            else:
                final = text[:i]

            result.update({'final': final})

    return result

# Additional functionalities specific to syllable processing can be added here
