from .config import Config
from .syllable import SyllableProcessor, Syllable
from typing import List
import numpy as np
import re
from functools import lru_cache


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
        self.text = text
        self.config = config
        self.ar = ar
        self.init_list = init_list
        self.fin_list = fin_list
        self.method = method
        # Syllable processor is initialized with the configuration and romanization method parameters
        self.syllable_processor = SyllableProcessor(config, ar, init_list, fin_list, method)
        self.chunks = []
        self._process_text()

    def _split_text_into_segments(self, text: str) -> List[str]:
        """
        Splits text into segments (words and non-text) based on the specified regex pattern.

        Args:
            text (str): The text to be split.

        Returns:
            List[str]: A list of split segments.
        """
        if self.config.error_skip:
            # Regular expression splits text into groups of words (including apostrophes and dashes) with
            # non-text elements separated
            pattern = r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)*|[^a-zA-ZüÜ]+"
        else:
            # Default pattern for word splitting, including apostrophes and dashes and excluding non-text elements
            # **FUTURE: Add error messages for non-text elements
            pattern = r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)*"
        return re.findall(pattern, text)

    def _split_word(self, word: str) -> List[str]:
        """
        Splits a word into smaller components based on the specified romanization method.

        Args:
            word (str): The word to be split.

        Returns:
            List[str]: A list of split components of the word.
        """
        if self.method == 'wg':
            # Splits string with respect to Wade-Giles's use of apostrophes in syllable initials
            pattern = r"[a-zA-ZüÜ]+(?:['’ʼ`][a-zA-ZüÜ]+)*"
        else:
            # Splits string
            pattern = r"[a-zA-ZüÜ]+|['’ʼ`\-–—][a-zA-ZüÜ]+"
        split_words = re.findall(pattern, word)
        return split_words if len(split_words) > 1 else [word]

    def _process_text(self):
        """
        Splits text into segments (words and non-text) and processes each segment into syllables or leaves it as is.

        Depending on the configuration, it can use different regex patterns for splitting the text.
        """
        # Collect segments using regular expressions
        segments = self._split_text_into_segments(self.text)
        for segment in segments:
            # Text elements are processed into syllables
            if re.match(r"[a-zA-ZüÜ]+", segment):
                # Regular expressions are used again to split words into smaller components
                split_words = self._split_word(segment)
                # Process each split word into Syllable objects
                self._process_split_words(split_words)
            else:
                # Non-text elements are directly appended as strings
                self.chunks.append(segment)
        # Print cache information to ensure proper usage
        # print(self._send_to_syllable_processor.cache_info())  # Displays cache statistics

    @lru_cache(maxsize=10000)
    def _send_to_syllable_processor(self, remaining_text: str) -> Syllable:
        """
        Sends the remaining text to the syllable processor to create a syllable object.

        Args:
            remaining_text (str): The remaining text to process.
        """
        return self.syllable_processor.create_syllable(remaining_text)
        # This commented code is for debugging purposes to print the resulting syllable object
        # result = self.syllable_processor.create_syllable(remaining_text)
        # print(result.__dict__)
        # return result

    def _process_split_words(self, split_words: List[str]):
        """
        Processes a list of split words into syllables, handling case detection and syllable creation.

        Args:
            split_words (List[str]): The split words to process.
        """
        syllables = []
        for syllable in split_words:
            remaining_text = syllable
            while remaining_text:
                # Send remaining text to syllable processor to create a syllable object
                syllable_obj = self._send_to_syllable_processor(remaining_text)
                syllables.append(syllable_obj)
                remaining_text = syllable_obj.remainder
        self.chunks.append(syllables)

    def get_chunks(self) -> List[List[Syllable]]:
        """
        Returns the processed chunks of text.

        Returns:
            List[Union[List[Syllable], str]]: A list of processed chunks where each chunk is either a list of Syllable
            objects or a string.
        """
        return self.chunks
