from typing import Tuple, Any, List
import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']

class Syllable:
    def __init__(self, text: str, config: Any, ar: np.ndarray, init_list: List[str], fin_list: List[str], remainder: str = ""):
        self.text = text
        self.remainder = remainder
        self.init_list = init_list
        self.fin_list = fin_list
        self.ar = ar
        self.config = config
        self.initial = ""
        self.final = ""
        self.full_syllable = ""
        self.valid = False
        self._process_syllable()

    def _process_syllable(self):
        self.initial, self.final, self.full_syllable, self.remainder = self._find_initial_final(self.text)
        self.valid = self._validate_syllable()

    def _find_initial_final(self, text: str) -> Tuple[str, str, str, str]:
        initial = self._find_initial(text)
        if initial == 'ø':
            return 'ø', text, text, ''

        final = self._find_final(text[len(initial):], initial)
        full_syllable = initial + final
        remainder = text[len(initial) + len(final):]
        return initial, final, full_syllable, remainder

    def _find_initial(self, text: str) -> str:
        for i, c in enumerate(text):
            if c in vowel:
                if i == 0:
                    return 'ø'
                initial = text[:i]
                if initial not in self.init_list:
                    return 'ø'
                return initial
        return 'ø'

    def _find_final(self, text: str, initial: str) -> str:
        for i, c in enumerate(text):
            if c in vowel:
                return self._handle_vowel_final(text, i)
            else:
                return self._handle_consonant_final(text, i, c, initial)
        return text

    def _handle_vowel_final(self, text: str, i: int) -> str:
        if i + 1 == len(text):
            return text

        for f_item in self.fin_list:
            if f_item.startswith(text[:i + 1]) and self._validate_final(f_item):
                return f_item
        return text[:i + 1]

    def _handle_consonant_final(self, text: str, i: int, c: str, initial: str) -> str:
        remainder = len(text) - i - 1

        if text[i - 1:i + 1] == 'er' and (remainder == 0 or text[i + 1] not in vowel):
            return text[:i] if len(text[:i]) > 1 else text[:i - 1]

        if c == 'n':
            return self._handle_n_final(text, i, initial, remainder)

        return text[:i]

    def _handle_n_final(self, text: str, i: int, initial: str, remainder: int) -> str:
        if remainder and text[i + 1] == 'g':
            if remainder < 2 or text[i + 2] not in vowel:
                return text[:i + 2]
            return text[:i + 1]

        if not remainder or text[i + 1] not in vowel:
            return text[:i + 1]
        return text[:i]

    def _validate_final(self, final: str) -> bool:
        initial_index = self.init_list.index(self.initial) if self.initial in self.init_list else -1
        final_index = self.fin_list.index(final) if final in self.fin_list else -1

        if initial_index == -1 or final_index == -1:
            return False

        return bool(self.ar[initial_index, final_index])

    def _validate_syllable(self) -> bool:
        return self._validate_final(self.final)