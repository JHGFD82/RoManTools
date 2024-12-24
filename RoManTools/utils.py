"""
Utilities for handling romanized Mandarin validation and conversion.

This module provides helper functions and methods used across the RoManTools package. It includes functionality for:
- Detecting romanization patterns.
- Validating input text.
- Segmenting text into syllables.
- Converting text between different romanization standards.
- Counting syllables in text.

Functions:
    segment_text(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False)
                 -> List[Union[List[Syllable], Syllable]]:
        Segments the given text into syllables based on the selected method.
    convert_text(text: str, convert_from: str, convert_to: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
        Converts the given text from one romanization standard to another.
    cherry_pick(text: str, convert_from: str, convert_to: str, crumbs: bool = False, error_skip: bool = True,
                error_report: bool = False) -> str:
        Converts the given text from one romanization standard to another if detected as a valid romanized Mandarin word.
    syllable_count(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False)
                   -> list[int]:
        Returns the count of syllables for each word in the processed text.
    detect_method(text: str, per_word: bool = False, crumbs: bool = False, error_skip: bool = False,
                  error_report: bool = False) -> Union[List[str], List[Dict[str, List[str]]]]:
        Detects the romanization method of the given text or individual words.
    validator(text: str, method: str, per_word: bool = False, crumbs: bool = False, error_skip: bool = False,
              error_report: bool = False) -> Union[bool, list[dict]]:
        Validates the processed text or individual words based on the selected method.

Usage Example:
    >>> from RoManTools import segment_text, convert_text, cherry_pick, syllable_count, detect_method, validator
    >>> segment_text("Zhongguo ti'an tianqi", method="py")
    [['zhong', 'guo'], ['ti', 'an'], ['tian', 'qi']]
    >>> convert_text("Zhongguo", convert_from="py", convert_to="wg")
    'Chung-kuo'
    >>> cherry_pick("This is Zhongguo.", convert_from="py", convert_to="wg")
    'This is Chung-kuo.'
    >>> syllable_count("Zhongguo", method="py")
    [2]
    >>> detect_method("Zhongguo")
    ['py']
    >>> validator("Zhongguo", method="py")
    True
"""

from functools import lru_cache
from typing import Dict, Union, List, Set, Optional
from .config import Config
from .chunker import TextChunkProcessor
from .syllable import Syllable
from .word import WordProcessor
from .data_loader import load_method_params, load_stopwords
# from memory_profiler import profile

__all__ = ['segment_text', 'convert_text', 'cherry_pick', 'syllable_count', 'detect_method', 'validator']


# Processing actions
@lru_cache(maxsize=1000000)
def _process_text(text: str, method: str, config: Config) -> List[Union[List[Syllable], Syllable]]:
    """
    Processes the given text using the specified method and configuration.

    Args:
        text (str): The text to be processed.
        method (str): The method to apply for text processing.
        config (Config): The configuration object containing processing settings.

    Returns:
        List[Union[List[Syllable], Syllable]]: A list of processed text chunks,
        which could be individual syllables or lists of syllables.
    """

    # if config.crumbs:
    #     print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, load_method_params(method))
    return processor.get_chunks()


# Segmentation actions
@lru_cache(maxsize=1000000)
def segment_text(text: str, method: str, config: Optional[Config] = None, **kwargs) \
        -> List[Union[List[Syllable], Syllable]]:
    """
    Segments the given text into syllables based on the selected method.

    Args:
        text (str): The text to be segmented.
        method (str): The method to apply for segmentation.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        List[Union[List[Syllable], Syllable]]: A list of segmented syllables or syllable chunks.

    Example:
        >>> text = "Zhongguo ti'an tianqi"
        >>> segment_text(text, method="py")
        [['zhong', 'guo'], ['ti', 'an'], ['tian', 'qi']]
    """

    if not config:
        config = Config(**kwargs)
    chunks = _process_text(text, method, config)
    segmented_result = []
    for chunk in chunks:
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            # Return the full syllable attribute for each Syllable object
            segmented_result.append([syl.text_attr.full_syllable for syl in chunk])
        else:
            # Return the non-text elements as strings
            segmented_result.append(chunk)
    return segmented_result


# Conversion actions
def _conversion_processing(text: str, convert: dict, config: Config, stopwords: Set[str], include_spaces: bool) \
        -> str:
    """
    Processes the given text for conversion between two romanization standards.

    Args:
        text (str): The text to be processed.
        convert (Dict[str, str]): The conversion mapping for the romanization standards.
        config (Config): The configuration object containing processing settings.
        stopwords (Set[str]): A set of stopwords to exclude from processing.
        include_spaces (bool): Whether to include spaces in the output.

    Returns:
        str: The converted text based on the selected romanization conversion mappings.
    """

    word_processor = WordProcessor(config, convert['from'], convert['to'], stopwords)
    concat_text = []
    for chunk in _process_text(text, convert['from'], config):
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            # When the chunk is a list of syllables, process them as a word, then append the result as strings
            word = word_processor.create_word(chunk)
            concat_text.append(word.process_syllables())
        else:
            # When the chunk is a string, append it to the result
            concat_text.append(chunk)
    # Return the concatenated text, with cherry_pick including spaces and symbols from original text,
    # and convert_text adding spaces between words
    return " ".join(concat_text) if include_spaces else "".join(concat_text)


@lru_cache(maxsize=1000000)
def convert_text(text: str, convert_from: str, convert_to: str, config: Optional[Config] = None, **kwargs) -> str:
    """
    Converts the given text from one romanization standard to another, returning errors for any invalid syllables.

    Args:
        text (str): The text to be converted.
        convert_from (str): The romanization standard to convert from.
        convert_to (str): The romanization standard to convert to.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        str: The converted text based on the selected romanization conversion mappings.

    Example:
        >>> text = "Zhongguo"
        >>> convert_text(text, convert_from="py", convert_to="wg")
        'Chung-kuo'
    """

    if not config:
        config = Config(**kwargs)
    stopwords = set(load_stopwords())
    convert = {"from": convert_from, "to": convert_to}
    return _conversion_processing(text, convert, config, stopwords, include_spaces=True)


@lru_cache(maxsize=1000000)
def cherry_pick(text: str, convert_from: str, convert_to: str, config: Optional[Config] = None, **kwargs) -> str:
    """
    Converts the given text from one romanization standard to another if detected as a valid romanized Mandarin word, and returns all over text.

    Args:
        text (str): The text to be converted.
        convert_from (str): The romanization standard to convert from.
        convert_to (str): The romanization standard to convert to.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        str: The converted text based on the selected romanization conversion mappings

    Example:
        >>> text = "This is Zhongguo."
        >>> cherry_pick(text, convert_from="py", convert_to="wg")
        'This is Chung-kuo.'
    """

    if not config:
        config = Config(error_skip=True, **kwargs)
    stopwords = set(load_stopwords())
    convert = {"from": convert_from, "to": convert_to}
    return _conversion_processing(text, convert, config, stopwords, include_spaces=False)


# Counting actions
@lru_cache(maxsize=1000000)
# @profile
def syllable_count(text: str, method: str, config: Optional[Config] = None, **kwargs) -> list[int]:
    """
    Returns the count of syllables for each word in the processed text.

    Args:
        text (str): The text to be processed.
        method (str): The method of romanization for the supplied text.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        List[int]: A list of lengths for each valid word in the processed text.

    Example:
        >>> text = "Zhongguo"
        >>> syllable_count(text, method="py")
        [2]
    """

    if not config:
        config = Config(**kwargs)
    chunks = _process_text(text, method, config)
    # Return the length of each chunk if all syllables are valid, otherwise return 0 (will change to error messages
    # in later update)
    return [lengths if all(syllable.valid for syllable in chunk) else 0 for chunk in chunks for lengths in [len(chunk)]]


# Detection and validation actions
@lru_cache(maxsize=1000000)
def detect_method(text: str, per_word: bool = False, config: Optional[Config] = None, **kwargs) \
        -> Union[List[str], List[Dict[str, List[str]]]]:
    """
    Detects the romanization method of the given text or individual words.

    Args:
        text (str): The text to be analyzed.
        per_word (bool, optional): Whether to report the possible romanization methods for each word. Defaults to False.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        Union[List[str], List[Dict[str, List[str]]]]: A list of detected methods, either for the full text or per word.

    Example:
        >>> text = "Zhongguo"
        >>> detect_method(text)
        ['py']
    """

    if not config:
        config = Config(**kwargs)
    methods = ['py', 'wg']

    def detect_for_chunk(chunk: str) -> List[str]:
        """
        Detects the valid processing methods for a given chunk of romanized Mandarin text.

        Args:
            chunk (str): A segment of romanized Mandarin text to be analyzed.

        Returns:
            List[str]: A list of methods that are valid for processing the given chunk.
        """

        result = []
        for method in methods:
            chunks = _process_text(chunk, method, config)
            if all(syllable.valid for chunk in chunks for syllable in chunk):
                result.append(method)
        return result

    if not per_word:
        # Perform detection for the entire text, returning a single list of valid methods
        return detect_for_chunk(text)
    # Perform detection per word, returning the valid methods for each word
    words = text.split()
    results = []
    for word in words:
        valid_methods = detect_for_chunk(word)
        results.append({"word": word, "methods": valid_methods})
    return results


@lru_cache(maxsize=1000000)
def validator(text: str, method: str, per_word: bool = False, config: Optional[Config] = None, **kwargs) \
        -> Union[bool, list[dict]]:
    """
    Validates the processed text or individual words based on the selected method.

    Args:
        text (str): The text to be validated.
        method (str): The method to apply for validation.
        per_word (bool, optional): Whether to report the validity of the entire text or each word. Defaults to False.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        Union[bool, list[dict]]: Validation results, either as a boolean for the entire text or a detailed list per
        word.

    Example:
        >>> text = "Zhongguo"
        >>> validator(text, method="py")
        True
    """

    if config is None:
        config = Config(**kwargs)
    chunks = _process_text(text, method, config)
    if not per_word:
        # Perform validation for the entire text, returning a single boolean value
        return all(syllable.valid for chunk in chunks for syllable in chunk)
    # Perform validation per word, returning the validity of each word
    result = []
    for word_chunks in chunks:
        word_result = {
            'word': ''.join(chunk.text_attr.full_syllable for chunk in word_chunks),
            'syllables': [chunk.text_attr.full_syllable for chunk in word_chunks],
            'valid': [chunk.valid for chunk in word_chunks]
        }
        result.append(word_result)
    return result
