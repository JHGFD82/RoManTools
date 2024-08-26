from typing import Dict, Union, List, Tuple
from .config import Config
from .chunk import TextChunkProcessor
from .syllable import Syllable
from .conversion import RomanizationConverter
from .data_loader import load_method_params, load_stopwords


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
    processor = TextChunkProcessor(text, config, **load_method_params(method, config))
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

    converted_words = []

    for chunk in chunks:
        converted_syllables = []
        for syllable in chunk:
            # Convert the syllable based on the specified method combination
            converted_text = converter.convert(syllable.full_syllable)

            # Reapply capitalization based on stored flags
            if syllable.uppercase:
                converted_text = converted_text.upper()
            elif syllable.capitalize:
                converted_text = converted_text.capitalize()

            converted_syllables.append(converted_text)

        # Join syllables back into a word and add it to the result
        converted_words.append("".join(converted_syllables))

    # Join words back into a single string and return the converted text
    return " ".join(converted_words)


def cherry_pick(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = False,
                error_report: bool = False) -> str:
    stopwords = load_stopwords()
    config, chunks = _setup_and_process(text, method_combination[:2], crumbs, error_skip, error_report)
    converter = RomanizationConverter(method_combination)
    converted_words = []

    for chunk in chunks:
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            # Perform the conversion process first, regardless of validity
            converted_syllables = []
            for syl in chunk:
                # Convert the syllable normally
                converted_text = converter.convert(syl.full_syllable)

                # Reapply capitalization based on stored flags
                if syl.uppercase:
                    converted_text = converted_text.upper()
                elif syl.capitalize:
                    converted_text = converted_text.capitalize()

                converted_syllables.append(converted_text)

            # Combine the syllables into a single word
            adjusted_word = ''.join(converted_syllables)

            # If the word is valid and not a stopword, use the converted version
            if all(syl.valid for syl in chunk) and adjusted_word.lower() not in stopwords:
                converted_words.append(adjusted_word)
            else:
                # If invalid, return the original syllables with capitalization preserved
                converted_words.append(''.join(syl.full_syllable for syl in chunk))
        else:
            # Non-Syllable text (e.g., punctuation) is returned as-is
            converted_words.append(chunk)

    return ''.join(converted_words)


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
