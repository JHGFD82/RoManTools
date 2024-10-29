from .config import Config
from typing import Tuple, List
import numpy as np
# from functools import lru_cache

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class SyllableProcessor:
    """
    Handles the loading of configuration settings and initializes data required for processing syllables.
    """

    def __init__(self, config: Config, ar: np.ndarray, init_list: List[str], fin_list: List[str], method: str):
        """
        Initializes the SyllableProcessor with configuration settings and lists for processing.

        Args:
            config (Config): The configuration object with settings like error_skip and crumbs.
            ar (np.ndarray): A NumPy array representing valid initial-final combinations.
            init_list (List[str]): A list of valid initial sounds.
            fin_list (List[str]): A list of valid final sounds.
            method (str): The romanization method being used ('py' for Pinyin, 'wg' for Wade-Giles).
        """
        self.config = config
        self.ar = ar
        self.init_list = init_list
        self.fin_list = fin_list
        self.method = method

    def create_syllable(self, text: str, remainder: str = "") -> "Syllable":
        """
        Creates a Syllable object based on the input text.

        Args:
            text (str): The input text to be processed into a syllable.
            remainder (str): The remainder of the input text to be processed into a syllable.

        Returns:
            Syllable: A Syllable object with information about the initial, final, and validity.
        """
        # result = Syllable(text, self, remainder)
        # print(result.__dict__)
        # return result
        return Syllable(text, self, remainder)


class Syllable:
    """
    Represents a syllable and its components (initial, final) in the context of a romanization method.
    """
    def __init__(self, text: str, processor: SyllableProcessor, remainder: str = ""):

        """
        Initializes a Syllable object with provided configuration and text.

        Args:
            text (str): The syllable text to be processed.
            remainder (str, optional): The remainder of the text to be processed. Defaults to "".
            processor (SyllableProcessor): The processor object used to validate the syllable.
        """
        self.text = text.lower()
        self.remainder = remainder
        self.processor = processor
        self.initial = ""
        self.final = ""
        self.full_syllable = ""
        self.valid = False
        self.apostrophes = ["'", "’", "ʼ", "`"]
        self.dashes = ["-", "–", "—"]
        self.has_apostrophe = False
        self.has_dash = False
        self.capitalize = text.istitle()
        self.uppercase = text.isupper()
        self._handle_first_char_symbols()
        self._process_syllable()

    def _handle_first_char_symbols(self):
        """
        Handles the first character of the text if it is an apostrophe or dash, updating the corresponding flags.

        Returns:
            str: The text with the first character removed if it was an apostrophe or dash.
        """

        if self.text[0] in self.apostrophes or self.text[0] in self.dashes:
            if self.text[0] in self.apostrophes:
                self.has_apostrophe = True
            elif self.text[0] in self.dashes:
                self.has_dash = True
            self.text = self.text[1:]

    def _process_syllable(self):
        """
        Processes the syllable to extract the initial, final, and remainder parts and validates the syllable.
        """
        self.initial, self.final, self.full_syllable, self.remainder = self._find_initial_final(self.text)
        self.valid = self._validate_syllable()

    def _find_initial_final(self, text: str) -> Tuple[str, str, str, str]:
        """
        Identifies the initial, final, and remainder of the given syllable text.

        Args:
            text (str): The input text to be split into initial, final, and remainder.

        Returns:
            Tuple[str, str, str, str]: The initial, final, full syllable, and remainder of the input text.
        """
        initial = self._find_initial(text)
        if initial == 'ø':
            final = self._find_final(text, initial)
            initial = ''
        else:
            final = self._find_final(text[len(initial):], initial)

        full_syllable = initial + final
        remainder_start = len(full_syllable)
        remainder = text[remainder_start:]

        return initial, final, full_syllable, remainder

    def _find_initial(self, text: str) -> str:
        """
        Extracts the initial component from the syllable text.

        Args:
            text (str): The syllable text to extract the initial from.

        Returns:
            str: The initial part of the syllable or 'ø' if no valid initial is found.
        """

        for i, c in enumerate(text):
            if c in vowel:
                if i == 0:
                    return 'ø'
                initial = text[:i]
                if initial not in self.processor.init_list:
                    return text[:i]
                return initial
            elif self.processor.method == 'wg' and c in self.apostrophes:
                return text[:i] + "'"  # ensure that the standard apostrophe is included in the initial

        return text

    def _find_final(self, text: str, initial: str) -> str:
        """
        Determines the final part of the syllable based on the input text.

        Args:
            text (str): The syllable text from which the final part is extracted.
            initial (str): The initial part of the syllable used for validation.

        Returns:
            str: The final part of the syllable.
        """
        if self.processor.method == 'py':
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
        elif self.processor.method == 'wg':
            return text

    def _handle_vowel_case(self, text: str, i: int, initial: str) -> str:
        """
        Handles cases where the final starts with a vowel.

        Args:
            text (str): The syllable text to be processed.
            i (int): The index of the vowel in the text.
            initial (str): The initial part of the syllable used for validation.

        Returns:
            str: The final part of the syllable or a subset based on potential candidates.
        """
        if i + 1 == len(text):
            return text  # This is a simple final with no further characters to process.

        # Iterate over the list of potential finals that start with the current vowel.
        test_finals = []
        for f_item in self.processor.fin_list:
            if f_item.startswith(text[:i + 1]) and self._validate_final(initial, f_item):
                test_finals.append(f_item)

        if not test_finals:
            if i == 0:
                pass
            else:
                return text[:i]

    def _handle_consonant_case(self, text: str, i: int, initial: str) -> str:
        """
        Handles cases where the final starts with a consonant, including special cases like "er", "n", and "ng".

        Args:
            text (str): The syllable text to be processed.
            i (int): The index of the consonant in the text.
            initial (str): The initial part of the syllable used for validation.

        Returns:
            str: The final part of the syllable.
        """
        remainder = len(text) - i - 1

        # Handle "er" and "erh"
        if text[i - 1:i + 1] == 'er':
            if remainder == 0 or (self.processor.method != 'wg' and text[i + 1] not in vowel):
                return text[:i + 1]
            elif self.processor.method == 'wg':
                if remainder > 0 and text[i + 1] == 'h':
                    return text[:i + 2]

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
                valid_n = remainder == 0 or text[i + 1] not in vowel or not self._validate_final(initial, text[:i])
                return text[:i + 1] if valid_n else text[:i]  # Return "n" or fall back

        # Default case: handle all other consonants
        return text[:i]

    # @lru_cache(maxsize=100000)
    def _validate_final(self, initial, final: str) -> bool:
        """
        Validates the final part of the syllable by checking against a predefined list of valid combinations.

        Args:
            initial (str): The initial part of the syllable.
            final (str): The final part of the syllable.

        Returns:
            bool: True if the final is valid, otherwise False.
        """
        initial_index = self.processor.init_list.index(initial) if initial in self.processor.init_list else -1
        final_index = self.processor.fin_list.index(final) if final in self.processor.fin_list else -1

        if initial_index == -1 or final_index == -1:
            return False

        return bool(self.processor.ar[initial_index, final_index])

    def _validate_syllable(self) -> bool:
        """
        Validates the overall syllable by checking the initial-final combination.

        Returns:
            bool: True if the syllable is valid, otherwise False.
        """
        if self.initial == '':
            return self._validate_final('ø', self.final)
        else:
            return self._validate_final(self.initial, self.final)
