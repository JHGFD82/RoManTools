"""
Syllable processing for romanized Mandarin text.

This module provides classes and methods for processing and validating syllables in romanized
Mandarin text. It includes functionality for:
- Initializing syllable processing with configuration settings.
- Creating and validating syllables.
- Handling different romanization methods (Pinyin and Wade-Giles).

Classes:
    SyllableProcessor: Handles the loading of configuration settings and initializes data required
                       for processing syllables.
    Syllable: Represents a syllable and its components (initial, final) in the context of a
              romanization method.
"""

# from functools import lru_cache
import re
from typing import Tuple, List, Optional
import numpy as np
from .config import Config
from .constants import vowels, apostrophes, dashes


class SyllableProcessor:
    """
    Handles the loading of configuration settings and initializes data required for processing
    syllables.
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
        self.has_apostrophe = False
        self.has_dash = False
        self.capitalize = False
        self.uppercase = text.isupper()
        self._is_titlecase(text)
        self._handle_first_char()
        self._process_syllable()

    def apply_caps(self, text: str) -> str:
        """
        Applies capitalization rules based on the syllable's properties.

        Args:
            text (str): The text to be transformed.

        Returns:
            str: The transformed text with applied capitalization.
        """
        if self.uppercase:
            return text.upper()
        if self.capitalize:
            return text.capitalize()
        return text

    def _is_titlecase(self, text: str):
        """
        Checks if the syllable text is in title case, considering contractions.

        Returns:
            bool: True if the text is in title case, considering contractions; otherwise, False.
        """
        # Remove all non-letter characters (.istitle() does not function properly with apostrophes and dashes)
        cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
        self.capitalize = cleaned_text.istitle()

    def _handle_first_char(self):
        """
        Handles the first character of the text if it is an apostrophe or dash, updating the corresponding flags.

        Returns:
            str: The text with the first character removed if it was an apostrophe or dash.
        """
        first_char = self.text[0]
        if first_char in apostrophes:
            self.has_apostrophe = True
        elif first_char in dashes:
            self.has_dash = True

        if (first_char in apostrophes and self.processor.method != 'wg') or first_char in dashes:
            self.text = self.text[1:]

    def _process_syllable(self):
        """
        Processes the syllable to extract the initial, final, and remainder parts and validates the syllable.
        """
        # Construct parts of syllable
        self.initial, self.final, self.full_syllable, self.remainder = self._find_initial_final(self.text)
        # Validate the syllable
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
        # If a "ø" is found, indicating no initial, find the final without the initial
        if initial == 'ø':
            final = self._find_final(text, initial)
            initial = ''
        else:
            final = self._find_final(text[len(initial):], initial)
        # After finding final, concatenate initial and final to get the full syllable
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
            if c in vowels:
                if i == 0:  # If a vowel is found at the beginning of the syllable, return 'ø' to indicate no initial
                    return 'ø'
                initial = text[:i]  # Otherwise, all text up to this point is the initial
                if initial not in self.processor.init_list:  # Check if the initial is valid
                    return text[:i]  # Return text up to this point if not valid
                return initial
            if self.processor.method == 'wg' and c in apostrophes:  # In cases of valid apostrophes in
                # Wade-Giles
                return text[:i] + "'"  # Ensure that the standard apostrophe is included in the initial

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
            return self._find_final_py(text, initial)
        if self.processor.method == 'wg':
            return self._find_final_wg(text)
        return text

    def _find_final_py(self, text: str, initial: str) -> str:
        """
        Handles the final part extraction for Pinyin method.

        Args:
            text (str): The syllable text to be processed.
            initial (str): The initial part of the syllable used for validation.

        Returns:
            str: The final part of the syllable.
        """
        for i, c in enumerate(text):
            # Handle cases where the final starts with a vowel or consonant, otherwise return whatever remaining
            # text is left
            if c in vowels:
                final = self._handle_vowel_case(text, i, initial)
                if final is not None:
                    return final
            else:
                return self._handle_consonant_case(text, i, initial)
        return text

    @staticmethod
    def _find_final_wg(text: str) -> str:
        """
        Handles the final part extraction for Wade-Giles method.

        Args:
            text (str): The syllable text to be processed.

        Returns:
            str: The final part of the syllable.
        """
        # FUTURE: expand on this to handle missing dashes (very likely), involves linking to _handle_consonant_case.
        for i, c in enumerate(text):
            if c in apostrophes:
                return text[:i]
        return text

    def _handle_vowel_case(self, text: str, i: int, initial: str) -> Optional[str]:
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
            return text  # This is a simple final with no further characters to process, usually in cases of no
            # consonants or multi-vowel finals
        # Iterate over the list of potential finals that start with the current vowel
        test_finals = []
        # Generate list of possible finals from this point in the text
        for f_item in self.processor.fin_list:
            if f_item.startswith(text[:i + 1]) and self._validate_final(initial, f_item):
                test_finals.append(f_item)
        # If no valid finals are found, return the text up to the vowel
        if not test_finals:
            if i == 0:
                return None
            up_to_vowel = text[:i]
            return up_to_vowel
        return None

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
            if remainder == 0 or (self.processor.method != 'wg' and text[i + 1] not in vowels):
                return text[:i + 1]
            # FUTURE: adjust logic below for Wade-Giles (currently unused)
            if self.processor.method == 'wg':
                if remainder > 0 and text[i + 1] == 'h':
                    return text[:i + 2]
        # Handle "n" and "ng"
        if text[i] == 'n':
            # Determine whether we are dealing with "ng" or just "n"
            next_char_is_g = remainder > 0 and text[i + 1] == 'g'
            # For possible "ng" cases, check if "g" is the last letter, if the next character after "g"
            # is a consonant, or if the current "n" final is invalid
            # This allows for "changan" to be split into "chan" and "gan" instead of "chang" and "an"
            valid_ng = next_char_is_g and (
                    remainder == 1 or text[i + 2] not in vowels or not self._validate_final(initial, text[:i + 1]))
            if valid_ng:
                return text[:i + 2]  # Return "ng"
            if next_char_is_g:
                return text[:i + 1]  # Return just "n" if the "ng" final isn't valid
            valid_n = remainder == 0 or text[i + 1] not in vowels or not self._validate_final(initial, text[:i])
            return text[:i + 1] if valid_n else text[:i]  # Return "n" or fall back to last vowel
        # Default case: handle all other consonants
        return text[:i]

    # @lru_cache(maxsize=100000)
    def _validate_final(self, initial, final: str) -> bool:
        """
        Validates the final part of the syllable by checking against a predefined list of valid combinations. This
        function is also referred to by _validate_syllable and is used to validate an entire syllable once it is fully
        determined.

        Args:
            initial (str): The initial part of the syllable.
            final (str): The final part of the syllable.

        Returns:
            bool: True if the final is valid, otherwise False.
        """
        # Indexes for both initial and final are both determined
        initial_index = self.processor.init_list.index(initial) if initial in self.processor.init_list else -1
        final_index = self.processor.fin_list.index(final) if final in self.processor.fin_list else -1
        # If no valid indexes are found, return False
        # FUTURE: Add custom error messages for invalid initials and finals (most likely no dashes for
        # multi-syllable Wade-Giles terms)
        if initial_index == -1 or final_index == -1:
            return False
        # Returns value found in the NumPy array
        return bool(self.processor.ar[initial_index, final_index])

    def _validate_syllable(self) -> bool:
        """
        Validates the overall syllable by checking the initial-final combination.

        Returns:
            bool: True if the syllable is valid, otherwise False.
        """
        # Syllable validation is performed by _validate_final, but is referenced here; "ø" supplied again for no initial
        if self.initial == '':
            return self._validate_final('ø', self.final)
        return self._validate_final(self.initial, self.final)