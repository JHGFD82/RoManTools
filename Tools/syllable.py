# syllable.py

import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    def __init__(self, text, ar, init_list, fin_list):
        self.text = text
        self.init_list = init_list
        self.fin_list = fin_list
        self.ar = ar
        self.config = config
        self.initial, self.final = self._find_initial_and_final()
        self.full_syl = (self.initial + self.final if self.initial[0] != 'ø'
                         else self.initial[1:] + self.final)
        self.length = len(self.full_syl)
        self.valid = self._validate_syllable(ar, init_list, fin_list)

    def _find_initial_and_final(self):
        initial = self._find_initial(self)
        if self.config.crumbs:
            print(f"{initial} [initial]")
        final = self._find_final(self, self.text[len(initial):])
        if self.config.crumbs:
            print(f"{initial}|{final} [final]")
        return initial, final

    @staticmethod
    def _find_initial(self):
        for i, c in enumerate(self.text):
            if c in vowel:
                if i == 0:
                    return 'ø'
                initial = self.text[:i]
                if initial not in self.init_list:
                    return 'ø'  # Marking invalid initial with 'ø'
                return initial

    @staticmethod
    def _find_final(self, text):
        length = len(text)

        for i, c in enumerate(text):
            if c in vowel:
                if i + 1 == length:
                    return text

                for f_item in (f for f in self.fin_list if f.startswith(text[:i + 1])):
                    if Syllable(f_item, self.ar, self.init_list, self.fin_list).valid:
                        return f_item

                return text[:i]

            else:
                remainder = length - i - 1

                if text[i - 1:i + 1] == 'er' and (remainder == 0 or text[i + 1] not in vowel):
                    return text[:i] if len(text[:i]) > 1 else text[:i - 1]

                elif c == 'n' and remainder > 0 and text[i + 1] == 'g':
                    if Syllable(text[:i + 1], self.ar, self.init_list, self.fin_list).valid:
                        return text[:i + 2] if remainder == 1 or text[i + 2] not in vowel else text[:i + 1]
                    return text[:i + 1]

                elif c == 'n':
                    return text[:i + 1] if remainder == 0 or text[i + 1] not in vowel else text[:i]

                else:
                    return text[:i]

        return text

    def _validate_syllable(self, ar, init_list, fin_list):
        try:
            init_index = init_list.index(self.initial)
            fin_index = fin_list.index(self.final)
            return ar[init_index, fin_index]
        except ValueError:
            return False
