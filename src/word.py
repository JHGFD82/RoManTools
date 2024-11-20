from typing import List, Set, Tuple
from .config import Config
from .syllable import Syllable
from .conversion import RomanizationConverter

class WordProcessor:
    """
    A class to process a word by converting its syllables and applying capitalization and symbols.
    """
    def __init__(self, config: Config, convert_from: str, convert_to: str, stopwords: Set[str]):
        self.config = config
        self.convert_from = convert_from
        self.convert_to = convert_to
        self.stopwords = stopwords
        self.converter = RomanizationConverter(f"{convert_from}_{convert_to}")

    def create_word(self, syllables: List[Syllable]) -> "Word":
        """
        Creates a Word object from a list of syllables.
        Args:
            syllables (List[Syllable]): A list of syllables to be processed.

        Returns:
            Word: A Word object created from the given syllables.
        """
        return Word(syllables, self)

class Word:
    def __init__(self, syllables: List[Syllable], processor: WordProcessor):
        self.syllables = syllables
        self.processor = processor
        self.processed_syllables = []
        self.supported_contractions = {"s", "d", "ll"}
        self.unsupported_contractions = {"m", "t"}
        self.preview_word = self._create_preview_word()
        self.final_word = ""
        self.valid = self.all_valid()
        self.contraction = self.is_contraction()

    def all_valid(self) -> bool:
        """
        Checks if all syllables in the word are valid by referencing the valid attribute of each syllable.

        Returns:
            bool: True if all syllables are valid, False otherwise
        """
        return all(syl.valid for syl in self.syllables)

    def is_contraction(self) -> bool:
        """
        Checks if the word is a contraction by verifying that the last syllable is not valid and has an apostrophe,
        and that the full syllable is in the supported contractions set. In the case of error_skip being False,
        allow the contraction to be processed as an error.

        Returns:
            bool: True if the word is a contraction, False otherwise
        """
        return all(syl.valid for syl in self.syllables[:-1]) and \
               (self.syllables[-1].has_apostrophe and self.syllables[-1].full_syllable in self.supported_contractions) \
            and self.processor.config.error_skip == True

    def _create_preview_word(self) -> str:
        """
        Creates a preview word by joining the full syllables of the word with apostrophes and dashes where necessary.

        Returns:
            str: The preview word
        """
        word_parts = []
        for syl in self.syllables:
            if syl.has_apostrophe:
                word_parts.append("'" + syl.full_syllable)
            elif syl.has_dash:
                word_parts.append("-" + syl.full_syllable)
            else:
                word_parts.append(syl.full_syllable)
        return "".join(word_parts)

    def convert(self):
        """
        Converts the syllables of the word, returning error messages for invalid syllables if error_skip is False.
        Otherwise, errors are ignored.

        Returns:
            Tuple[str, Syllable]: A tuple containing the converted syllable and the original syllable
        """
        if not self.processor.config.error_skip: # For standard conversion requests
            self.processed_syllables = [(self.processor.converter.convert(syl.full_syllable), syl) for syl in self.syllables]
        elif (self.valid or self.contraction) and self.preview_word not in self.processor.stopwords: # For cherry_pick
            self.processed_syllables = [
                (self.processor.converter.convert(syl.full_syllable), syl) if syl.valid else (syl.full_syllable, syl)
                for syl in self.syllables
            ]
        else:
            self.processed_syllables = [(syl.full_syllable, syl) for syl in self.syllables]

    def apply_caps(self):
        """
        Applies capitalization to the converted syllables.

        Returns:
            Tuple[str, Syllable]: A tuple containing the capitalized syllable and the original syllable
        """
        self.processed_syllables = [(syl[1].apply_caps(syl[0]), syl[1]) for syl in self.processed_syllables]

    def add_symbols(self):
        """
        Adds apostrophes and dashes to the converted syllables based on the conversion system and the presence of vowels.

        Returns:
            str: The final word with added symbols
        """
        vowels = {'a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ'}
        if (self.valid or self.contraction) and self.preview_word not in self.processor.stopwords:
            self.final_word = self.processed_syllables[0][0]
            for i in range(1, len(self.processed_syllables)):
                self._append_syllable(i, vowels)
        else:
            self._append_all_syllables()

    def _append_syllable(self, i: int, vowels: Set[str]):
        """
        Appends a syllable to the final word with an apostrophe or a dash based on the conversion system and the
        presence of vowels.

        Args:
            i (int): The index of the syllable to be appended
            vowels (Set[str]): A set of vowels used to determine whether an apostrophe is needed

        Returns:
            None
        """
        prev_syllable = self.processed_syllables[i - 1][0]
        curr_syllable = self.processed_syllables[i][0]
        if self.processor.convert_to == 'py' and self.processed_syllables[i][1].valid:
            if self._needs_apostrophe(prev_syllable, curr_syllable, vowels):
                self.final_word += "'" + curr_syllable
            else:
                self.final_word += curr_syllable
        elif self.processor.convert_to == 'wg':
            self.final_word += "'" + curr_syllable if self.contraction and i == len(
                self.processed_syllables) - 1 else "-" + curr_syllable

    def _append_all_syllables(self):
        """
        Appends all syllables to the final word without adding any symbols.

        Returns:
            None
        """
        for syl in self.processed_syllables:
            if syl[1].has_apostrophe:
                self.final_word += "'" + syl[0]
            elif syl[1].has_dash:
                self.final_word += "-" + syl[0]
            else:
                self.final_word += syl[0]

    @staticmethod
    def _needs_apostrophe(prev_syllable: str, curr_syllable: str, vowels: Set[str]) -> bool:
        """
        Determines whether an apostrophe is needed between two syllables based on the last character of the previous
        syllable and the first character of the current syllable.

        Args:
            prev_syllable (str): The previous syllable
            curr_syllable (str): The current syllable
            vowels (Set[str]): A set of vowels used to determine whether an apostrophe is needed

        Returns:
            bool: True if an apostrophe is needed, False otherwise
        """
        return (prev_syllable[-1] in vowels and curr_syllable[0] in vowels) or \
            (prev_syllable.endswith('er') and curr_syllable[0] in vowels) or \
            (prev_syllable[-1] == 'n' and curr_syllable[0] in vowels) or \
            (prev_syllable.endswith('ng') and curr_syllable[0] in vowels)

    def process_syllables(self) -> str:
        """
        Processes the syllables of the word by converting them, applying capitalization, and adding symbols.

        Returns:
            str: The final word after processing the syllables
        """
        self.convert()
        self.apply_caps()
        self.add_symbols()
        return self.final_word
