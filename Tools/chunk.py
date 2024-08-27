from .config import Config
from .syllable import SyllableProcessor, Syllable
from typing import List, Tuple
import numpy as np
import re


class TextChunkProcessor:
    """
    Processes text into chunks for further processing based on the specified romanization method (e.g., Pinyin,
    Wade-Giles).

    Attributes:
        text (str): The input text to be processed.
        config (Config): Configuration object that manages processing options like crumbs, error skipping, and error
        reporting.
        ar (np.ndarray): The array used for validating initial-final combinations.
        init_list (List[str]): The list of valid initials.
        fin_list (List[str]): The list of valid finals.
        method (str): The romanization method being used ("py" for Pinyin or "wg" for Wade-Giles).
        syllable_processor (SyllableProcessor): The processor used to handle syllable creation and validation.
        chunks (List[Union[List[Syllable], str]]): The processed chunks of text, where each chunk is either a list of
        syllables or a string.
    """
    def __init__(self, text: str, config: Config, ar: np.ndarray, init_list: List[str], fin_list: List[str],
                 method: str):
        """
        Initializes the TextChunkProcessor with the input text, configuration, and method details.

        Args:
            text (str): The input text to be processed.
            config (Config): Configuration object that manages processing options.
            ar (np.ndarray): The array used for validating initial-final combinations.
            init_list (List[str]): The list of valid initials.
            fin_list (List[str]): The list of valid finals.
            method (str): The romanization method ("py" for Pinyin or "wg" for Wade-Giles).
        """
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
    def _detect_case(word: str) -> Tuple[str, bool, bool]:
        """
        Detects the case (title case or uppercase) of a syllable and returns the lowercase version.

        Args:
            word (str): The syllable to analyze.

        Returns:
            Tuple[str, bool, bool]: A tuple containing the lowercased syllable, a boolean indicating if it is title
            case, and a boolean indicating if it is uppercase.
        """
        is_title_case = word.istitle()  # Detect if the word is title-cased (first letter capitalized)
        is_uppercase = word.isupper()  # Detect if the word is fully uppercase
        lowercased_word = word.lower()  # Convert the word to lowercase for processing
        return lowercased_word, is_title_case, is_uppercase

    def _split_word(self, word: str) -> List[str]:
        """
        Splits a word into smaller components based on the specified romanization method.

        Args:
            word (str): The word to be split.

        Returns:
            List[str]: A list of split components of the word.
        """
        if self.method == "wg":
            # For Wade-Giles, split words using hyphens (including en-dash and em-dash)
            split_words = re.split(r"[\-–—]", word)
        else:
            # For Pinyin or other systems, split on a broader range of delimiters
            split_words = re.split(r"[‘’'ʼ`\-–—]", word)

        return split_words if len(split_words) > 1 else [word]

    def _process_chunks(self):
        """
        Splits text into segments (words and non-text) and processes each segment into syllables or leaves it as is.

        Depending on the configuration, it can use different regex patterns for splitting the text.
        """
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
        """
        Processes a list of split words into syllables, handling case detection and syllable creation.

        Args:
            split_words (List[str]): The split words to process.
        """
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
        """
        Returns the processed chunks of text.

        Returns:
            List[Union[List[Syllable], str]]: A list of processed chunks where each chunk is either a list of Syllable
            objects or a string.
        """
        return self.chunks
