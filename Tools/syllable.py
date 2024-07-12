# syllable.py

import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    def __init__(self, **kwargs):
        self.initial = kwargs['initial']
        self.final = kwargs['final']
        self.full_syl = (self.initial + self.final if self.initial[0] != 'ø'
                         else self.initial[1:] + self.final)
        self.length = len(self.full_syl)

        try:
            result = kwargs['ar'][kwargs['init_list'].index(self.initial),
            kwargs['fin_list'].index(self.final)]
        except ValueError:
            self.valid = False
        else:
            self.valid = result


def find_initial(text, **kwargs):
    initial = ''
    result = {}

    for i, c in enumerate(text):
        if c in vowel:
            if i == 0:
                result.update({'initial': 'ø'})
            else:
                initial = text[:i]
                if initial not in kwargs['init_list']:
                    result.update({'initial': initial, 'error': initial + ': invalid initial'})
                else:
                    result.update({'initial': initial})
            return result

    if not initial:
        result.update({'initial': text, 'error': text + ': no final'})
        return result


def find_final(text, **kwargs):
    result = {}

    for i, c in enumerate(text):
        if c in vowel and i + 1 == len(text):
            result.update({'final': text})
            return result

        elif c in vowel and i > 0:
            test_syls = []
            for f_item in list(l for l in kwargs['fin_list'] if l.startswith(text[:i + 1])):
                kwargs.update({'final': f_item})
                test_syls.append(Syllable(**kwargs).valid)
            if True not in test_syls:
                result.update({'final': text[:i]})
                return result

        elif c not in vowel:
            remainder = len(text) - i - 1
            if (text[i - 1:i + 1] == 'er' and (not remainder or text[i + 1] not in vowel)):
                final = text[:-2] if len(text[:i]) > 1 else text[:i - 1]
            elif c == 'n':
                if remainder and text[i + 1] == 'g':
                    kwargs.update({'final': text[:i + 1]})
                    final = text[:i + 2] if (remainder < 2 or text[i + 2] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i + 1]
                else:
                    kwargs.update({'final': text[:i]})
                    final = text[:i + 1] if (not remainder or text[i + 1] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i]
            else:
                final = text[:i]

            result.update({'final': final})
            return result
