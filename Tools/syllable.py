from typing import Tuple, Any, List
import numpy as np

vowel = ['a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ']


class Syllable:
    """
    This class represents a syllable in the Chinese language. It is used to process and validate syllables based on
    provided configuration.

    Parameters:
    - text: The input text representing the syllable.
    - config: The configuration object used for processing and validating syllables.
    - ar: A NumPy ndarray representing the vowel-conditioned acceptance-rejection array.
    - init_list: A list of initial characters.
    - fin_list: A list of final characters.
    - method: The method used for processing syllables (e.g., "wg" for Wade-Giles).
    - remainder: An optional remainder string for further processing after syllable extraction.

    Attributes:
    - text: The input text representing the syllable.
    - remainder: The remaining text after extracting the syllable.
    - init_list: The list of initial characters.
    - fin_list: The list of final characters.
    - ar: The vowel-conditioned acceptance-rejection array.
    - method: The method used for processing syllables.
    - initial: The extracted initial character(s) of the syllable.
    - final: The extracted final character(s) of the syllable.
    - full_syllable: The full syllable string (initial + final).
    - valid: A boolean indicating whether the syllable is valid or not.

    Methods:
    - _process_syllable(): Processes the input syllable by extracting the initial and final characters, and validating
    the syllable.
    - _find_initial_final(text: str) -> Tuple[str, str, str, str]: Finds the initial and final characters of the given
    text.
    - _find_initial(text: str) -> str: Finds the initial character(s) of the given text.
    - _find_final(text: str, initial: str) -> str: Finds the final character(s) of the given text, given the initial
    character(s).
    - _handle_vowel_case(text: str, i: int, initial: str) -> str: Handles the case where the current character is a
    vowel.
    - _handle_consonant_case(text: str, i: int, initial: str) -> str: Handles the case where the current character is a
    consonant.
    - _validate_final(initial, final: str) -> bool: Validates whether the combination of initial and final characters is
    valid.
    - _validate_syllable() -> bool: Validates whether the syllable is valid.

    """
    def __init__(self, text: str, config: Any, ar: np.ndarray, init_list: List[str], fin_list: List[str], method: str,
                 remainder: str = ""):
        self.text = text
        self.remainder = remainder
        self.init_list = init_list
        self.fin_list = fin_list
        self.ar = ar
        self.method = method
        self.config = config
        self.initial = ""
        self.final = ""
        self.full_syllable = ""
        self.valid = False
        self._process_syllable()

    def _process_syllable(self):
        """

        Process a syllable to find its initial, final, full syllable, and remaining text.

        Returns:
            None

        """
        self.initial, self.final, self.full_syllable, self.remainder = self._find_initial_final(self.text)
        self.valid = self._validate_syllable()

    def _find_initial_final(self, text: str) -> Tuple[str, str, str, str]:
        """

        Method Name: _find_initial_final

        Parameters:
        - text: str
          - Description: The input text string from which to find the initial, final, full syllable, and remainder.
          - Type: str

        Return Type: Tuple[str, str, str, str]
          - Description: A tuple containing the initial, final, full syllable, and remainder of the text string.
          - Type: Tuple[str, str, str, str]

        Description:
        This method finds the initial, final, full syllable, and remainder of a given text string. The initial is
        determined by calling the "_find_initial" method, and if it returns 'ø', the final is determined by calling the
        "_find_final" method with the entire text string. In this case, the initial is set to an empty string. If the
        initial is not 'ø', the final is determined by calling the "_find_final" method with the remaining portion of
        the text string after removing the initial. The full syllable is a concatenation of the initial and final, and
        the remainder is the remaining text string after removing the initial and final.

        Example Usage:
        ```python
        text = "example text"
        initial, final, full_syllable, remainder = self._find_initial_final(text)
        print("Initial:", initial)
        print("Final:", final)
        print("Full Syllable:", full_syllable)
        print("Remainder:", remainder)
        ```

        """
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
        """

        Find the initial consonant cluster in a given text.

        Parameters:
        - text (str): The input text to find the initial consonant cluster from.

        Returns:
        - str: The initial consonant cluster found in the text.

        """
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
        """

        Method: _find_final

        This method is used to find the final consonant or vowel in a given text. It takes two parameters: text (str) and initial (str). It returns the final consonant or vowel found in the text.

        Parameters:
        - text (str): The input text in which the final consonant or vowel needs to be found.
        - initial (str): The initial consonant or vowel that was already found before the final consonant or vowel.

        Return:
        - str: The final consonant or vowel found in the text.

        """
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
        """

        Handles the vowel case when processing text.

        Parameters:
        - text (str): The input text to be processed.
        - i (int): The index of the current character being processed.
        - initial (str): The initial character of the text.

        Returns:
        - str: The processed text.

        This method handles cases where the current character being processed is a vowel. It checks if there are any
        potential finals that start with the current vowel. If there are no valid finals found, it will return the text
        up to the previous character index.

        If the current character is the last character in the text, it will simply return the input text as there are no
        further characters to process.

        """
        if i + 1 == len(text):
            return text  # This is a simple final with no further characters to process.

        # Iterate over the list of potential finals that start with the current vowel.
        test_finals = []
        for f_item in self.fin_list:
            if f_item.startswith(text[:i + 1]) and self._validate_final(initial, f_item):
                test_finals.append(f_item)
        if not test_finals:
            if i == 0:
                pass
            else:
                return text[:i]

    def _handle_consonant_case(self, text: str, i: int, initial: str) -> str:
        """

        Handles consonants when they appear while processing text.

        Parameters:
        - text (str): The input text.
        - i (int): The index of the current character in the text.
        - initial (str): The initial character of the text.

        Return:
        - str: The modified text based on the handling of consonant cases.

        Description:
        This method handles different cases for consonants in the input text. It takes three parameters: the input text,
        the index of the current character, and the initial character of the text. It returns the modified text based on
        the handling of consonant cases.

        The method first calculates the remainder by subtracting the current index `i` from the length of the text.

        Next, it checks for specific cases:

        1. "er" and "erh" case:
           - If the characters at index `i-1` and `i` are equal to "er", it proceeds with further checks.
           - If the remainder is 0 or the method is not "wg" and the character at index `i+1` is not a vowel, it returns
           the text up to index `i+1`.
           - If the method is "wg" and the remainder is 1 and the character at index `i+1` is "h", it returns the text
           up to index `i+2`.

        2. "h" case with Wade-Giles method:
           - If the character at index `i` is "h" and the method is "wg":
              - It checks if the remainder is 0, or the character at index `i+1` is not a vowel, or the
              `_validate_final` method returns false for the initial character and the text up to index `i`.
              - If any of the above conditions are true, it returns the text up to index `i+1`, otherwise, it falls back
              by returning the text up to index `i`.

        3. "n" and "ng" case:
           - If the character at index `i` is "n":
              - It checks whether the next character is "g" to determine whether it's "ng" or just "n".
              - If the next character is "g" and the remainder is 1 or the character at index `i+2` is not a vowel, or
              the `_validate_final` method returns false for the initial character and the text up to index `i+1`, it
              returns the text up to index `i+2` (returning "ng").
              - If the next character is "g" but the conditions above are not met, it returns the text up to index `i+1`
              (returning just "n").
              - If the next character is not "g", it checks if the remainder is 0, or the character at index `i+1` is
              not a vowel, or the `_validate_final` method returns false for the initial character and the text up to
              index `i`.
              - If any of the above conditions are true, it returns the text up to index `i+1` (returning "n"),
              otherwise, it falls back by returning the text up to index `i`.

        4. Default case:
           - For all other consonants, it returns the text up to index `i`.

        """
        remainder = len(text) - i - 1

        # Handle "er" and "erh"
        if text[i - 1:i + 1] == 'er':
            if remainder == 0 or (self.method != 'wg' and text[i + 1] not in vowel):
                return text[:i + 1]
            elif self.method == 'wg':
                if remainder == 1 and text[i + 1] == 'h':
                    return text[:i + 2]

        # Handle "h" with Wade-Giles
        elif text[i] == 'h' and self.method == 'wg':
            valid_h = remainder == 0 or text[i + 1] not in vowel or not self._validate_final(initial, text[:i])
            return text[:i + 1] if valid_h else text[:i]  # Return "h" or fall back

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

    def _validate_final(self, initial, final: str) -> bool:
        """

        The `_validate_final` method is used to validate if the given `initial` and `final` values are present in the
        `init_list` and `fin_list`, respectively.

        Parameters:
        - `initial`: A value of type `str` representing the initial value.
        - `final`: A value of type `str` representing the final value.

        Returns:
        - A value of type `bool`. Returns `True` if both `initial` and `final` values are present in their respective
        lists and there is a valid connection between them in the matrix `ar`. Returns `False` otherwise.

        """
        initial_index = self.init_list.index(initial) if initial in self.init_list else -1
        final_index = self.fin_list.index(final) if final in self.fin_list else -1

        if initial_index == -1 or final_index == -1:
            return False

        return bool(self.ar[initial_index, final_index])

    def _validate_syllable(self) -> bool:
        """

        Validates the syllable based on the initial and final components.

        Returns:
            bool: True if the syllable is valid, False otherwise.

        """
        if self.initial == '':
            return self._validate_final('ø', self.final)
        else:
            return self._validate_final(self.initial, self.final)
