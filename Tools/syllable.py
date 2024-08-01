# syllable.py

import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    def __init__(self, initial, final, ar, init_list, fin_list):
        self.initial = initial
        self.final = final
        self.full_syl = (self.initial + self.final if self.initial[0] != 'ø'
                         else self.initial[1:] + self.final)
        self.length = len(self.full_syl)
        self.valid = self._validate_syllable(ar, init_list, fin_list)

    def _validate_syllable(self, ar, init_list, fin_list):
        try:
            init_index = init_list.index(self.initial)
            fin_index = fin_list.index(self.final)
            return ar[init_index, fin_index]
        except ValueError:
            return False


def find_initial(text, init_list):
    for i, c in enumerate(text):
        if c in vowel:
            if i == 0:
                return {'initial': 'ø'}
            initial = text[:i]
            if initial not in init_list:
                return {'initial': initial, 'error': f'{initial}: invalid initial'}
            return {'initial': initial}
    return {'initial': text, 'error': f'{text}: no final'}


def find_final(text, fin_list, ar, init_list):
    result = {}
    length = len(text)

    for i, c in enumerate(text):
        # Case: Vowel found
        if c in vowel:
            # Case: Single vowel at the end
            if i + 1 == length:
                result.update({'final': text})
                return result

            # Case: Test all possible final syllables starting with the current text segment
            for f_item in (f for f in fin_list if f.startswith(text[:i + 1])):
                kwargs = {'initial': 'ø', 'final': f_item, 'ar': ar, 'init_list': init_list, 'fin_list': fin_list}
                if Syllable(**kwargs).valid:
                    result.update({'final': f_item})
                    return result

            # No valid final found starting with the current text segment
            result.update({'final': text[:i]})
            return result

        # Case: Non-vowel found
        else:
            remainder = length - i - 1

            # Special Case: "er"
            if text[i - 1:i + 1] == 'er' and (remainder == 0 or text[i + 1] not in vowel):
                final = text[:i] if len(text[:i]) > 1 else text[:i - 1]
                result.update({'final': final})
                return result

            # Special Case: "ng"
            elif c == 'n' and remainder > 0 and text[i + 1] == 'g':
                kwargs = {'initial': 'ø', 'final': text[:i + 1], 'ar': ar, 'init_list': init_list, 'fin_list': fin_list}
                if Syllable(**kwargs).valid:
                    final = text[:i + 2] if remainder == 1 or text[i + 2] not in vowel else text[:i + 1]
                else:
                    final = text[:i + 1]
                result.update({'final': final})
                return result

            # Special Case: "n"
            elif c == 'n':
                final = text[:i + 1] if remainder == 0 or text[i + 1] not in vowel else text[:i]
                result.update({'final': final})
                return result

            # Default Case: Regular non-vowel final
            else:
                final = text[:i]
                result.update({'final': final})
                return result

    # No valid final found
    result.update({'final': text, 'error': f'{text}: no valid final found'})
    return result
