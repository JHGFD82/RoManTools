# syllable.py
from typing import Tuple, Any, List
import numpy as np
import copy

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    def __init__(self, text: str, config: Any, ar: np.ndarray, init_list: List[str], fin_list: List[str]):
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

    def _find_initial_and_final(self) -> Tuple[str, str]:
        initial = self._find_initial(self)
        if self.config.crumbs:
            print(f"{initial} [initial]")
        final = self._find_final(self, self.text[len(initial):])
        if self.config.crumbs:
            print(f"{initial}|{final} [final]")
        return initial, final

    @staticmethod
    def _find_initial(self) -> str:
        for i, c in enumerate(self.text):
            if c in vowel:
                if i == 0:
                    return 'ø'
                initial = self.text[:i]
                if initial not in self.init_list:
                    return 'ø'  # Marking invalid initial with 'ø'
                return initial

    @staticmethod
    def _find_final(self, text) -> str:
        recursive_config = self._prepare_recursive_config()

        # Check if the final syllable is a vowel-based or a special case like 'er', 'ng'
        for i, c in enumerate(text):
            if c in vowel:
                return self._handle_vowel_case(text, i, recursive_config)
            return self._handle_non_vowel_case(text, i, recursive_config)
        return text

    def _prepare_recursive_config(self) -> Any:
        recursive_config = copy.deepcopy(self.config)
        recursive_config.crumbs = False
        return recursive_config

    def _handle_vowel_case(self, text: str, i: int, recursive_config: Any) -> str:
        if i + 1 == len(text):
            return text

        for f_item in self.fin_list:
            if f_item == text[:len(f_item)]:
                if Syllable(f_item, recursive_config, self.ar, self.init_list, self.fin_list).valid:
                    return f_item

        return text

    def _handle_non_vowel_case(self, text: str, i: int, recursive_config: Any):
        remainder = len(text) - i - 1

        if text[i - 1:i + 1] == 'er' and (remainder == 0 or text[i + 1] not in vowel):
            return text[:i] if len(text[:i]) > 1 else text[:i - 1]

        if c == 'n' and remainder > 0 and text[i + 1] == 'g':
            if Syllable(text[:i + 1], recursive_config, self.ar, self.init_list, self.fin_list).valid:
                return text[:i + 2] if remainder == 1 or text[i + 2] not in vowel else text[:i + 1]
            return text[:i + 1]

        if c == 'n':
            return text[:i + 1] if remainder == 0 or text[i + 1] not in vowel else text[:i]

        return text

    def _validate_syllable(self, ar: np.ndarray, init_list: List[str], fin_list: List[str]) -> bool:
        try:
            init_index = init_list.index(self.initial)
            fin_index = fin_list.index(self.final)
            return bool(ar[init_index, fin_index])
        except ValueError:
            return False
