from typing import List, Set, Tuple
from .config import Config
from .syllable import Syllable
from .constants import vowels, supported_contractions
from .conversion import RomanizationConverter

class WordProcessor:
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
        self.preview_word = self._create_preview_word()
        self.final_word = ""
        self.valid = self.all_valid()
        self.contraction = self.is_contraction()

    def _create_preview_word(self) -> str:
        """
        Creates a preview word by joining the full syllables of the word with apostrophes and dashes where necessary.
        The preview word is used to determine whether the word is a stopword, which includes contractions such as
        "we've" and "we're," which are potentially valid romanized syllables, even though they are not Mandarin terms.

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
               (self.syllables[-1].has_apostrophe and self.syllables[-1].full_syllable in supported_contractions) \
            and self.processor.config.error_skip == True

    def is_convertable(self) -> bool:
        """
        Checks if the word is valid or a contraction and not a stopword.

        Returns:
            bool: True if the word is valid or a contraction and not a stopword, False otherwise
        """
        return (self.valid or self.contraction) and self.preview_word not in self.processor.stopwords

    def convert(self):
        """
        Converts the syllables of the word, returning error messages for invalid syllables if error_skip is False.
        Otherwise, errors are ignored.

        Returns:
            Tuple[str, Syllable]: A tuple containing the converted syllable and the original syllable
        """
        # For standard conversion requests, process syllables with error messages.
        if not self.processor.config.error_skip:
            self.processed_syllables = [(self.processor.converter.convert(syl.full_syllable), syl) for syl in self.syllables]
        # Otherwise, process syllables without error messages, specifically for the cherry_pick action.
        # Convert the syllables if all are valid, or are part of a contraction, and the whole word is not a stopword.
        # The last syllable will fail conversion, but no error message will be produced and the self.contraction
        # attribute will be used later to allow proper processing of contractions.
        elif self.is_convertable():
            self.processed_syllables = [
                (self.processor.converter.convert(syl.full_syllable), syl) if syl.valid else (syl.full_syllable, syl)
                for syl in self.syllables
            ]
        # If this is for cherry_pick and there are an invalid number of valid syllables, and the word is not a
        # stopword, process syllables without conversion or error messages (allows English words to pass through).
        else:
            self.processed_syllables = [(syl.full_syllable, syl) for syl in self.syllables]

    def apply_caps(self):
        """
        Applies capitalization to the converted syllables.

        Returns:
            Tuple[str, Syllable]: A tuple containing the capitalized syllable and the original syllable
        """
        # The apply_caps method within the Syllable object is called on each syllable to apply capitalization based on
        # titlecase or uppercase attributes within each syllable.
        self.processed_syllables = [(syl[1].apply_caps(syl[0]), syl[1]) for syl in self.processed_syllables]

    def add_symbols(self):
        """
        Adds apostrophes and dashes to the converted syllables based on the conversion system and the presence of vowels.

        Returns:
            str: The final word with added symbols
        """
        # Syllables have to be processed individually if conversion took place. Otherwise, they are combined in a
        # different process.
        if self.is_convertable():
            self.final_word = self.processed_syllables[0][0]
            for i in range(1, len(self.processed_syllables)):
                self._append_syllable(i)
        else:
            self._append_all_syllables()

    def _append_syllable(self, i: int):
        """
        Appends a syllable to the final word with an apostrophe or a dash based on the conversion system and the
        presence of vowels.

        Args:
            i (int): The index of the syllable to be appended

        Returns:
            None
        """
        # Specific rules for romanization are contained here.
        prev_syllable = self.processed_syllables[i - 1][0]
        curr_syllable = self.processed_syllables[i][0]
        # For Pinyin, specific logic is applied to determine whether an apostrophe is needed between syllables.
        if self.processor.convert_to == 'py' and self.processed_syllables[i][1].valid:
            if self._needs_apostrophe(prev_syllable, curr_syllable):
                self.final_word += "'" + curr_syllable
            else:
                self.final_word += curr_syllable
        # For Wade-Giles, dashes are used to separate syllables except if this happens to be a contraction
        # as part of the cherry_pick action.
        elif self.processor.convert_to == 'wg':
            self.final_word += "'" + curr_syllable if self.contraction and i == len(
                self.processed_syllables) - 1 else "-" + curr_syllable

    @staticmethod
    def _needs_apostrophe(prev_syllable: str, curr_syllable: str) -> bool:
        """
        Determines whether an apostrophe is needed between two syllables based on the last character of the previous
        syllable and the first character of the current syllable.

        Args:
            prev_syllable (str): The previous syllable
            curr_syllable (str): The current syllable

        Returns:
            bool: True if an apostrophe is needed, False otherwise
        """
        # The logic for apostrophes in Pinyin is based on the following rules in which the start of the next syllable
        # is a vowel:
        # - If the last character of the previous syllable and the first character of the current syllable is a vowel
        # - If the previous syllable ends with 'er', 'n', or 'ng'
        return (prev_syllable[-1] in vowels and curr_syllable[0] in vowels) or \
            (prev_syllable.endswith('er') and curr_syllable[0] in vowels) or \
            (prev_syllable[-1] == 'n' and curr_syllable[0] in vowels) or \
            (prev_syllable.endswith('ng') and curr_syllable[0] in vowels)

    def _append_all_syllables(self):
        """
        Appends all syllables to the final word, adding any symbols if they were in the original text.

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