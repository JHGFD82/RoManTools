from .config import Config
from .syllable import SyllableProcessor, Syllable
from typing import List, Tuple
import numpy as np
import re


class TextChunkProcessor:
    """
    The TextChunkProcessor class represents a processor for text chunks. It splits the input text into chunks and
    processes each chunk into a list of syllables.

    Attributes:
    - text: The input text (str)
    - config: The configuration object (Config)
    - ar: The numpy array (np.ndarray)
    - init_list: The list of initial sounds (List[str])
    - fin_list: The list of final sounds (List[str])
    - method: The processing method (str)
    - chunks: The list of processed chunks (List[List[Syllable]])

    Methods:
    - __init__(text: str, config: Config, ar: np.ndarray, init_list: List[str], fin_list: List[str], method: str):
    Initializes a new instance of the TextChunkProcessor class. It sets the input parameters and calls the
    _process_chunks method to process the chunks.
    - _split_word(word: str) -> List[str]: Splits a word into a list of split words based on the processing method.
    Returns the split words.
    - _process_split_words(split_words: List[str]): Processes the split words into syllables. Appends the syllables to
    the chunks list.
    - _process_chunks(): Splits the input text into words using regular expressions. Calls the _split_word and
    _process_split_words methods for each word.
    - get_chunks() -> List[List[Syllable]]: Returns the list of processed chunks.

    Example usage:
    config = Config(...)
    ar = np.ndarray(...)
    init_list = ['...', '...']
    fin_list = ['...', '...']
    method = '...'
    text = '...'

    processor = TextChunkProcessor(text, config, ar, init_list, fin_list, method)
    chunks = processor.get_chunks()
    """
    def __init__(self, text: str, config: Config, ar: np.ndarray, init_list: List[str], fin_list: List[str],
                 method: str):
        self.text = text
        self.config = config
        self.ar = ar
        self.init_list = init_list
        self.fin_list = fin_list
        self.method = method
        self.syllable_processor = SyllableProcessor(config, ar, init_list, fin_list, method)
        self.chunks = []
        self._process_chunks()

    @staticmethod
        """
        Detects the case of the word and returns it in lowercase along with two boolean flags indicating if the word
        was capitalized (title case) or uppercase.

        :param word: The word to detect case for.
        :return: A tuple (lowercased word, is_title_case, is_uppercase).
        """
        is_title_case = word.istitle()  # Detect if the word is title-cased (first letter capitalized)
        is_uppercase = word.isupper()  # Detect if the word is fully uppercase
        lowercased_word = word.lower()  # Convert the word to lowercase for processing
        return lowercased_word, is_title_case, is_uppercase

    def _split_word(self, word: str) -> List[str]:
        if self.method == "wg":
            # For Wade-Giles, split words using hyphens (including en-dash and em-dash)
            split_words = re.split(r"[\-–—]", word)
        else:
            # For Pinyin or other systems, split on a broader range of delimiters
            split_words = re.split(r"[‘’'ʼ`\-–—]", word)

        return split_words if len(split_words) > 1 else [word]

    def _process_chunks(self):
        if self.config.error_skip:
            # Use a comprehensive regex to split text into words and non-text
            pattern = r"([a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)?|[^a-zA-ZüÜ]+)"
        else:
            # Default pattern for standard word splitting
            pattern = r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)?"

        segments = re.findall(pattern, self.text)

        for segment in segments:
            if re.match(r"[a-zA-ZüÜ]+", segment):
                split_words = self._split_word(segment)
                self._process_split_words(split_words)
            else:
                # Non-text elements are directly appended as strings
                self.chunks.append(segment)

    def _process_split_words(self, split_words: List[str]):
        syllables = []
        for syllable in split_words:
            lowercased_syllable, is_title_case, is_uppercase = self._detect_case(syllable)

            remaining_text = lowercased_syllable
            first_syllable = True  # Track if we're processing the first syllable

            while remaining_text:
                syllable_obj = self.syllable_processor.create_syllable(remaining_text)
                syllable_obj.uppercase = False
                # Apply capitalization rules based on the detected case
                if is_uppercase:
                    syllable_obj.uppercase = True
                elif first_syllable and is_title_case:
                    syllable_obj.capitalize = True
                else:
                    syllable_obj.capitalize = False

                syllables.append(syllable_obj)
                remaining_text = syllable_obj.remainder

                # After processing the first syllable, subsequent syllables should no longer be title case
                first_syllable = False

        self.chunks.append(syllables)

    def get_chunks(self) -> List[List[Syllable]]:
        return self.chunks