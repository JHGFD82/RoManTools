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
from typing import Dict, Union, List, Set, Optional, Sequence
from .config import Config
from .chunker import TextChunkProcessor
from .syllable import Syllable
from .word import WordProcessor
from .data_loader import load_method_params, load_stopwords
from .constants import shorthand_to_full
# from memory_profiler import profile

__all__ = ['segment_text', 'convert_text', 'cherry_pick', 'syllable_count', 'detect_method', 'validator']


# Processing actions
@lru_cache(maxsize=1000000)
def _process_text(text: str, method: str, config: Config) -> Sequence[Union[Sequence[Syllable], Syllable, str]]:
    """
    Processes the given text using the specified method and configuration.

    Args:
        text (str): The text to be processed.
        method (str): The method to apply for text processing.
        config (Config): The configuration object containing processing settings.

    Returns:
        Sequence[Union[Sequence[Syllable], Syllable, str]]: A sequence of processed text chunks,
        which could be individual syllables, sequences of syllables, or strings.
    """

    # if config.crumbs:
    #     print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, load_method_params(method))
    return processor.get_chunks()


# Segmentation actions
def segment_text(text: str, method: str, config: Optional[Config] = None, **kwargs: bool) \
        -> List[Union[List[str], str]]:
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

    @lru_cache(maxsize=1000000)
    def _cached_segment_text(config_info: Optional[Config] = None) -> List[Union[List[str], str]]:
        """
        Segments the given text using the cached segmentation logic.
        Args:
            config_info: The configuration object containing processing settings. Defaults to None.

        Returns:
            Sequence[Union[Sequence[Syllable], Syllable]]: A sequence of segmented syllables or syllable chunks.
        """
        if not config_info:
            config_info = Config(**kwargs)
        chunks = _process_text(text, method, config_info)
        segmented_result: List[Union[List[str], str]] = []
        config_info.print_crumb(1, 'Segment Text', 'Assembling segments', True)
        for chunk in chunks:
            if isinstance(chunk, list):
                # Return the full syllable attribute for each Syllable object
                segmented_result.append([syl.text_attr.full_syllable for syl in chunk])
            elif isinstance(chunk, str):
                # Return the non-text elements as strings
                segmented_result.append(chunk)
            else:
                # In all oher cases, raise an error
                raise ValueError(f"Unexpected chunk type: {type(chunk)} in segment_text")
        return segmented_result

    if kwargs or (config and any([config.crumbs, config.error_skip, config.error_report])):
        return _cached_segment_text.__wrapped__(config)
    return _cached_segment_text()


# Conversion actions
def _conversion_processing(text: str, convert: Dict[str, str], config: Config, stopwords: Set[str], include_spaces: bool) \
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
    concat_text: List[str] = []
    for chunk in _process_text(text, convert['from'], config):
        if isinstance(chunk, list):
            # When the chunk is a list of syllables, process them as a word, then append the result as strings
            word = word_processor.create_word(chunk)
            concat_text.append(word.process_syllables())
        elif isinstance(chunk, str):
            # When the chunk is a string, append it to the result
            concat_text.append(chunk)
        else:
            # In all other cases, raise an error
            raise ValueError(f"Unexpected chunk type: {type(chunk)} in _conversion_processing")
    config.print_crumb(footer=True)
    # Return the concatenated text, with cherry_pick including spaces and symbols from original text,
    # and convert_text adding spaces between words
    return " ".join(concat_text) if include_spaces else "".join(concat_text)


def convert_text(text: str, convert_from: str, convert_to: str, config: Optional[Config] = None, **kwargs: bool) -> str:
    """
    Converts the given text from one romanization standard to another, returning errors for any invalid syllables.

    Args:
        text (str): The text to be converted.
        convert_from (str): The romanization standard to convert from.
        convert_to (str): The romanization standard to convert to.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.
        **kwargs: Additional keyword arguments to initialize the Config object if not provided.

    Returns:
        str: The converted text based on the selected romanization conversion mappings.

    Example:
        >>> text = "Zhongguo"
        >>> convert_text(text, convert_from="py", convert_to="wg")
        'Chung-kuo'
    """

    @lru_cache(maxsize=1000000)
    def _cached_convert_text(config_info: Optional[Config] = None) -> str:
        """
        Converts the given text using the cached conversion logic.

        Args:
            config_info (Config, optional): The configuration object containing processing settings. Defaults to None.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """
        if not config_info:
            config_info = Config(**kwargs)
        stopwords = set(load_stopwords())
        convert = {"from": convert_from, "to": convert_to}
        result = _conversion_processing(text, convert, config_info, stopwords, include_spaces=True)
        return result

    if kwargs or (config and any([config.crumbs, config.error_skip, config.error_report])):
        return _cached_convert_text.__wrapped__(config)
    return _cached_convert_text()


def cherry_pick(text: str, convert_from: str, convert_to: str, config: Optional[Config] = None, **kwargs: bool) -> str:
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

    @lru_cache(maxsize=1000000)
    def _cached_cherry_pick(config_info: Optional[Config] = None) -> str:
        """
        Converts the given text using the cached cherry-pick logic.

        Args:
            config_info (Config, optional): The configuration object containing processing settings. Defaults to None.

        Returns:
            str: The converted text based on the selected romanization conversion mappings.
        """
        if not config_info:
            config_info = Config(error_skip=True, **kwargs)
        stopwords = set(load_stopwords())
        convert = {"from": convert_from, "to": convert_to}
        return _conversion_processing(text, convert, config_info, stopwords, include_spaces=False)

    if kwargs or (config and any([config.crumbs, config.error_report])):
        return _cached_cherry_pick.__wrapped__(config)
    return _cached_cherry_pick()


# Counting actions
# @profile
def syllable_count(text: str, method: str, config: Optional[Config] = None, **kwargs: bool) -> list[int]:
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

    @lru_cache(maxsize=1000000)
    def _cached_syllable_count(config_info: Optional[Config] = None) -> list[int]:
        """
        Counts the syllables for each word in the processed text using the cached logic.

        Args:
            config_info (Config, optional): The configuration object containing processing settings. Defaults to None.

        Returns:
            List[int]: A list of lengths for each valid word in the processed text.
        """
        if not config_info:
            config_info = Config(**kwargs)
        chunks = _process_text(text, method, config_info)
        config_info.print_crumb(1, 'Syllable Count', 'Assembling counts', True)
        # Return the length of each chunk if all syllables are valid, otherwise return 0 (will change to error messages
        # in later update)
        return [len(chunk) for chunk in chunks if isinstance(chunk, list)]

    if kwargs or (config and any([config.crumbs, config.error_skip, config.error_report])):
        return _cached_syllable_count.__wrapped__(config)
    return _cached_syllable_count()


# Detection and validation actions
def detect_method(text: str, per_word: bool = False, config: Optional[Config] = None, **kwargs: bool) \
        -> Union[List[str], List[Dict[str, Union[str, List[str]]]]]:
    """
    Detects the romanization method of the given text or individual words.

    Args:
        text (str): The text to be analyzed.
        per_word (bool, optional): Whether to report the possible romanization methods for each word. Defaults to False.
        config (Config, optional): The configuration object containing processing settings. Defaults to None.

    Returns:
        Union[List[str], List[Dict[str, Union[str, List[str]]]]]: A list of detected methods, either for the full text or per word.

    Example:
        >>> text = "Zhongguo"
        >>> detect_method(text)
        ['py']
    """

    @lru_cache(maxsize=1000000)
    def _cached_detect_method(config_info: Optional[Config] = None) -> Union[List[str], List[Dict[str, Union[str, List[str]]]]]:
        """
        Detects the romanization method of the given text using the cached detection logic.

        Args:
            config_info (Config, optional): The configuration object containing processing settings. Defaults to None.

        Returns:
            Union[List[str], List[Dict[str, List[str]]]]: A list of detected methods, either for the full text or per word.
        """

        if not config_info:
            config_info = Config(**kwargs)

        def detect_for_chunk(chunk: str, crumbs: bool = False) -> List[str]:
            """
            Detects the valid processing methods for a given chunk of romanized Mandarin text.

            Args:
                chunk (str): A segment of romanized Mandarin text to be analyzed.
                crumbs (bool, optional): Whether to include intermediate outputs (crumbs) during processing. Defaults to False.

            Returns:
                List[str]: A list of methods that are valid for processing the given chunk.
            """

            result: List[str] = []
            for method in shorthand_to_full.keys():
                processed_chunks = _process_text(chunk, method, config_info)
                syllable_chunks: List[Syllable] = []
                for processed_chunk in processed_chunks:
                    if isinstance(processed_chunk, list):
                        for syllable in processed_chunk:
                            syllable_chunks.append(syllable)
                if syllable_chunks and all(syllable.valid for syllable in syllable_chunks):
                    result.append(method)
            if crumbs:
                config_info.print_crumb(1, 'Detect Method', 'Assembling methods for all syllables', True)
            return result

        if not per_word:
            # Perform detection for the entire text, returning a single list of valid methods
            return detect_for_chunk(text, True)
        # Perform detection per word, returning the valid methods for each word
        words = text.split()
        results: List[Dict[str, Union[str, List[str]]]] = []
        for word in words:
            valid_methods = detect_for_chunk(word)
            results.append({"word": word, "methods": valid_methods})
        config_info.print_crumb(1, 'Detect Method', 'Assembling methods', True)
        return results

    if kwargs or (config and any([config.crumbs, config.error_skip, config.error_report])):
        return _cached_detect_method.__wrapped__(config)
    return _cached_detect_method()


def validator(text: str, method: str, per_word: bool = False, config: Optional[Config] = None, **kwargs: bool) \
        -> Union[bool, list[dict[str, Union[str, list[str], list[bool]]]]]:
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

    @lru_cache(maxsize=1000000)
    def _cached_validator(config_info: Optional[Config] = None) -> Union[bool, List[Dict[str, Union[str, List[str], List[bool]]]]]:
        """
        Validates the processed text or individual words using the cached validation logic.

        Args:
            config_info: The configuration object containing processing settings. Defaults to None.

        Returns:
            Union[bool, list[dict]]: Validation results, either as a boolean for the entire text or a detailed list per word.
        """

        if config_info is None:
            config_info = Config(**kwargs)
        chunks = _process_text(text, method, config_info)
        syllable_chunks: List[Syllable] = []
        for chunk in chunks:
            if isinstance(chunk, list):
                for syllable in chunk:
                    syllable_chunks.append(syllable)
        if not per_word:
            # Perform validation for the entire text, returning a single boolean value
            return all(syllable.valid for syllable in syllable_chunks)
        # Perform validation per word, returning the validity of each word
        result: List[Dict[str, Union[str, List[str], List[bool]]]] = []
        for chunk in chunks:
            if isinstance(chunk, list):
                word_result: Dict[str, Union[str, List[str], List[bool]]] = {
                    'word': ''.join(syl.text_attr.full_syllable for syl in chunk),
                    'syllables': [syl.text_attr.full_syllable for syl in chunk],
                    'valid': [bool(syl.valid) for syl in chunk]
                }
                result.append(word_result)
        return result

    if kwargs or (config and any([config.crumbs, config.error_skip, config.error_report])):
        return _cached_validator.__wrapped__(config)
    return _cached_validator()
