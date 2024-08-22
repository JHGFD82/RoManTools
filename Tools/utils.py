# utils.py
import re
import os
from typing import Dict, Union, List, Tuple
import numpy as np
from .syllable import Syllable
from .conversion import RomanizationConverter
from .data_loader import load_romanization_data, load_stopwords

base_path = os.path.dirname(__file__)


class Config:
    """

    Config class represents a configuration object with three boolean attributes: crumbs, error_skip, and error_report.

    Attributes:
        crumbs (bool): Indicates whether to enable or disable the generation of crumbs.
        error_skip (bool): Indicates whether to skip errors or raise exceptions when encountered.
        error_report (bool): Indicates whether to generate error reports.

    Methods:
        __init__(crumbs: bool = False, error_skip: bool = False, error_report: bool = False)
            Initializes a new instance of the Config class with the specified attributes.

    Example usage:
        # Create a new Config object with default values
        config = Config()

        # Create a new Config object with specific attribute values
        config = Config(crumbs=True, error_skip=False, error_report=True)

    """
    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report


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
        self.chunks = []
        self._process_chunks()

    def _split_word(self, word: str) -> List[str]:
        if self.method == "wg":
            # For Wade-Giles, split words using hyphens (including en-dash and em-dash)
            split_words = re.split(r"[\-–—]", word)
        else:
            # For Pinyin or other systems, split on a broader range of delimiters
            split_words = re.split(r"[‘’'ʼ`\-–—]", word)

        return split_words if len(split_words) > 1 else [word]

    def _process_split_words(self, split_words: List[str]):
        syllables = []
        for syllable in split_words:
            remaining_text = syllable

            while remaining_text:
                syllable_obj = Syllable(remaining_text, self.config, self.ar, self.init_list, self.fin_list,
                                        self.method)
                syllables.append(syllable_obj)
                remaining_text = syllable_obj.remainder

        self.chunks.append(syllables)

    def _process_chunks(self):
        words = re.findall(r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)?", self.text)

        for word in words:
            split_words = self._split_word(word)
            self._process_split_words(split_words)

    def get_chunks(self) -> List[List[Syllable]]:
        return self.chunks


def _get_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
    """

    Get method parameters for the given method and configuration.

    Parameters:
        method (str): The name of the method.
        config (Config): The configuration object.

    Returns:
        dict: A dictionary containing the following keys:
            - 'ar' (numpy.ndarray): The AR parameter.
            - 'init_list' (list of str): The initial list parameter.
            - 'fin_list' (list of str): The final list parameter.
            - 'method' (str): The method parameter.

    """
    method_file = f'{method}DF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method_file}.csv'))

    if config.crumbs:
        print(f"# {method.upper()} romanization data loaded #")

    return {
        'ar': ar,
        'init_list': init_list,
        'fin_list': fin_list,
        'method': method
    }


def _process_text(text: str, method: str, config: Config) -> List[Union[List[Syllable], Syllable]]:
    """

    Processes the given text using the specified method and configuration.

    Parameters:
    text (str): The text to be processed.
    method (str): The method to be used for processing.
    config (Config): The configuration settings for the processing.

    Returns:
    List[Union[List[Syllable], Syllable]]: The processed chunks of text.

    """
    if config.crumbs:
        print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, **_get_method_params(method, config))
    return processor.get_chunks()


def _setup_and_process(text: str, method: str, crumbs: bool = False, error_skip: bool = False,
                       error_report: bool = False) -> Tuple[Config, List[Union[List[Syllable], Syllable]]]:
    """

    Sets up the configuration and processes the given text using the specified method.

    Args:
        text (str): The text to be processed.
        method (str): The method to be used for processing.
        crumbs (bool, optional): Whether to include breadcrumbs in the configuration. Defaults to False.
        error_skip (bool, optional): Whether to skip errors during processing. Defaults to False.
        error_report (bool, optional): Whether to include error reporting in the configuration. Defaults to False.

    Returns:
        Tuple[Config, List[Union[List[Syllable], Syllable]]]: A tuple consisting of the configuration object and
                                                            the list of processed text chunks.

    """
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)
    chunks = _process_text(text, method, config)
    return config, chunks


def segment_text(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False) \
        -> List[Union[List[Syllable], Syllable]]:
    """
    Segment the given text into syllables.

    Parameters:
        text (str): The input text to be segmented into syllables.
        method (str): The method to be used for segmentation. Possible values are:
            - "pinyin", "py"
            - "wade-giles", "wg"
        crumbs (bool, optional): If True, include partial syllables at the end of each chunk. Defaults to False.
        error_skip (bool, optional): If True, skip to the next chunk if an error occurs while processing a chunk.
        Defaults to False.
        error_report (bool, optional): If True, include error information in the output. Defaults to False.

    Returns:
        List[Union[List[Syllable], Syllable]]: A nested list of syllables. Each inner list corresponds to a chunk of the
        input text,
        and contains either a list of syllables or a single syllable object.

    """
    config, chunks = _setup_and_process(text, method, crumbs, error_skip, error_report)

    return [[chunk.full_syllable for chunk in chunks] for chunks in chunks]


def convert_text(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
    """

    Converts a text into a processed result using specific method combination.

    Parameters:
        text (str): The input text to be processed.
        method_combination (str): The method combination to be used for processing.
        crumbs (bool, optional): Determines whether to include crumbs in the result. Defaults to False.
        error_skip (bool, optional): Determines whether to skip errors during processing. Defaults to False.
        error_report (bool, optional): Determines whether to include error reports in the result. Defaults to False.

    Returns:
        str: The processed result text.

    """
    config, chunks = _setup_and_process(text, method_combination[:2], crumbs, error_skip, error_report)

    converter = RomanizationConverter(method_combination)

    result = ' '.join(
        ''.join(converter.convert(syllable.full_syllable) for syllable in chunk) if isinstance(chunk, list)
        else converter.convert(chunk.full_syllable) for chunk in chunks
    )

    return result.strip()


def cherry_pick(words: str, convert, converter):
    stopwords = load_stopwords(os.path.join(base_path, 'data', 'stopwords.txt'))
    converted_words = []

    for word in words:
        adjusted_word = ''.join(syl.full_syl for syl in word)
        valid_word = all(syl.valid for syl in word)

        if valid_word and adjusted_word not in stopwords:
            adjusted_word = '-'.join(converter.convert(syl.full_syl, convert) for syl in word)

        if 'cap' in word[0].__dict__:
            adjusted_word = adjusted_word.capitalize()

        converted_words.append(adjusted_word)

    return ' '.join(converted_words)


def syllable_count(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False) \
        -> list[int]:
    """

    Count the number of syllables in the given text using the specified method.

    Args:
        text (str): The input text for which the syllable count needs to be calculated.
        method (str): The method to use for syllable counting.
        crumbs (bool, optional): Flag to indicate if syllable crumbs should be generated. Default is False.
        error_skip (bool, optional): Flag to indicate if erroneous words should be skipped. Default is False.
        error_report (bool, optional): Flag to indicate if erroneous words should be reported. Default is False.

    Returns:
        list[int]: A list of syllable counts. Returns 0 if any syllable in a chunk is invalid, otherwise returns the
        length of each chunk.

    """
    config, chunks = _setup_and_process(text, method, crumbs, error_skip, error_report)

    return [lengths if all(syllable.valid for syllable in chunk) else 0 for chunk in chunks for lengths in [len(chunk)]]


def detect_method(text: str, per_word: bool = False, crumbs: bool = False, error_skip: bool = False,
                  error_report: bool = False) -> Union[List[str], List[Dict[str, List[str]]]]:
    """

    Detects valid methods for a given text.

    Parameters:
    - text: A string representing the text to be analyzed.
    - per_word: A boolean specifying whether detection should be performed per word or for the whole text. Default is
    False.
    - crumbs: A boolean indicating whether to include "crumbs" in the analysis. Default is False.
    - error_skip: A boolean indicating whether to skip words with errors during analysis. Default is False.
    - error_report: A boolean indicating whether to include error reports in the analysis. Default is False.

    Returns:
    - If per_word is False, returns a list of valid methods for the whole text.
    - If per_word is True, returns a list of dictionaries, where each dictionary contains a word and its corresponding
    valid methods.

    Note: The valid methods are determined based on the given text and the specified parameters.

    Example usage:

    # Detection for the whole text
    valid_methods = detect_method("ni hao")
    print(valid_methods)  # Output: ['py', 'wg']

    # Detection per word
    results = detect_method("ni hao", per_word=True)
    print(results)  # Output: [{'word': 'ni', 'methods': ['py', 'wg']}, {'word': 'hao', 'methods': ['py', 'wg']}]

    """
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)
    methods = ['py', 'wg']

    def detect_for_chunk(chunk: str) -> List[str]:
        """

        Detects the presence of specific methods in a given chunk of text.

        Parameters:
        - chunk (str): The chunk of text to be analyzed.

        Returns:
        - result (List[str]): A list of methods detected in the chunk.

        """
        result = []
        for method in methods:
            chunks = _process_text(chunk, method, config)
            if all(syllable.valid for chunk in chunks for syllable in chunk):
                result.append(method)
        return result

    if per_word:
        # Perform detection per word
        words = text.split()  # Split by spaces
        results = []
        for word in words:
            valid_methods = detect_for_chunk(word)
            results.append({"word": word, "methods": valid_methods})
        return results
    else:
        # Perform detection for the whole text
        valid_methods = detect_for_chunk(text)
        return valid_methods


def validator(text: str, method: str, per_word: bool = False, crumbs: bool = False, error_skip: bool = False,
              error_report: bool = False) -> Union[bool, list[dict]]:
    """

    This method validates a given text using a specific validation method.

    Parameters:
    - text (str): The text to be validated.
    - method (str): The validation method to be used.
    - per_word (bool, optional): Flag indicating whether to return detailed information per word (default: False).
    - crumbs (bool, optional): Flag indicating whether to process crumbs for validation (default: False).
    - error_skip (bool, optional): Flag indicating whether to skip validation on error (default: False).
    - error_report (bool, optional): Flag indicating whether to report errors during validation (default: False).

    Returns:
    - bool: True if all syllables are valid (when per_word is False).
    - list[dict]: Detailed information per word, including the word, its syllables, and their validity
    (when per_word is True).

    """
    config, chunks = _setup_and_process(text, method, crumbs, error_skip, error_report)

    if not per_word:
        return all(syllable.valid for chunk in chunks for syllable in chunk)

    # Return detailed information per word
    result = []
    for word_chunks in chunks:
        word_result = {
            'word': ''.join(chunk.full_syllable for chunk in word_chunks),
            'syllables': [chunk.full_syllable for chunk in word_chunks],
            'valid': [chunk.valid for chunk in word_chunks]
        }
        result.append(word_result)

    return result
