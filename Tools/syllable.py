from typing import Tuple, Any, List
import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    def __init__(self, text: str, config: Any, ar: np.ndarray, init_list: List[str], fin_list: List[str],
                 remainder: str = ""):
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
            final = self._find_final(text, initial)
            initial = ''
        else:
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
                    return text[:i]
                return initial
        return text

    def _find_final(self, text: str, initial: str) -> str:
        for i, c in enumerate(text):
            if c in vowel:
                final = self._handle_vowel_case(text, i, initial)
                if final is None:
                    pass
                else:
                    return final
            else:
                return self._handle_consonant_case(text, i, initial)
        return text

    def _handle_vowel_case(self, text: str, i: int, initial: str) -> str:
        if i + 1 == len(text):
            return text  # This is a simple final with no further characters to process.

        # Iterate over the list of potential finals that start with the current vowel.
        test_finals = []
        for f_item in self.fin_list:
            if f_item.startswith(text[:i + 1]) and self._validate_final(initial, f_item):
                test_finals.append(f_item)

        if not test_finals:
            return text[:i]

    def _handle_consonant_case(self, text: str, i: int, initial: str) -> str:
        remainder = len(text) - i - 1

        # Handle "er" and "erh"
        if text[i - 1:i + 1] == 'er' and (remainder == 0 or text[i + 1] not in vowel):
            return text[:-2] if len(text[:i]) > 1 else text[:i - 1]

        # Handle "n" and "ng"
        elif text[i] == 'n':
            # Determine whether we are dealing with "ng" or just "n"
            next_char_is_g = remainder > 0 and text[i + 1] == 'g'
            valid_ng = next_char_is_g and (
                        remainder == 1 or text[i + 2] not in vowel or not self._validate_final(initial, text[:i + 1]))

            if valid_ng:
                return text[:i + 2]  # Return "ng"
            elif next_char_is_g:
                return text[:i + 1]  # Return just "n" if the "g" isn't valid
            else:
                valid_n = remainder == 0 or text[i + 1] not in vowel or not self._validate_final(initial, text[:i + 1])
                return text[:i + 1] if valid_n else text[:i]  # Return "n" or fall back

        # Default case: handle all other consonants
        return text[:i]

    def _validate_final(self, initial, final: str) -> bool:
        initial_index = self.init_list.index(initial) if initial in self.init_list else -1
        final_index = self.fin_list.index(final) if final in self.fin_list else -1

        if initial_index == -1 or final_index == -1:
            return False

        return bool(self.ar[initial_index, final_index])

    def _validate_syllable(self) -> bool:
        if self.initial == '':
            return self._validate_final('ø', self.final)
        else:
            return self._validate_final(self.initial, self.final)
