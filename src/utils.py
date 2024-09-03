from typing import Dict, Union, List, Tuple
from .config import Config
from .chunk import TextChunkProcessor
from .syllable import Syllable
from .conversion import RomanizationConverter
from .data_loader import load_method_params, load_stopwords


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
    if config.crumbs:
        print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, **load_method_params(method, config))
    return processor.get_chunks()


def _setup_and_process(text: str, method: str, crumbs: bool = False, error_skip: bool = False,
                       error_report: bool = False) -> Tuple[Config, List[Union[List[Syllable], Syllable]]]:
    """
    Sets up the configuration and processes the text.

    Args:
        text (str): The text to be processed.
        method (str): The method to apply for text processing.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        Tuple[Config, List[Union[List[Syllable], Syllable]]]: A tuple containing the configuration and the processed
        chunks.
    """
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)
    chunks = _process_text(text, method, config)

    return config, chunks


def _apply_caps(text: str, syl: Syllable) -> str:
    """
    Applies capitalization rules based on the syllable's properties.

    Args:
        text (str): The text to be transformed.
        syl (Syllable): The syllable object containing capitalization rules.

    Returns:
        str: The transformed text with applied capitalization.
    """
    if syl.uppercase:
        return text.upper()
    elif syl.capitalize:
        return text.capitalize()
    return text


def segment_text(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False) \
        -> List[Union[List[Syllable], Syllable]]:
    """
    Segments the given text into syllables based on the selected method.

    Args:
        text (str): The text to be segmented.
        method (str): The method to apply for segmentation.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        List[Union[List[Syllable], Syllable]]: A list of segmented syllables or syllable chunks.

    Example:
        >>> text = "Zhongguo"
        >>> segment_text(text, method="py")
        [['zhong', 'guo']]
    """
    config, chunks = _setup_and_process(text, method, crumbs, error_skip, error_report)

    segmented_result = []

    for chunk in chunks:
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            # Return the full syllable attribute for each Syllable object
            segmented_result.append([syl.full_syllable for syl in chunk])
        else:
            # Return the non-text elements as strings
            segmented_result.append(chunk)

    return segmented_result


def convert_text(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
    """
    Converts the given text using the specified method combination.

    Args:
        text (str): The text to be converted.
        method_combination (str): The combination of romanization methods, converting from the first and to the second.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        str: The converted text.

    Example:
        >>> text = "Zhongguo"
        >>> convert_text(text, method_combination="py-wg")
        'Chung-kuo'
    """
    config, chunks = _setup_and_process(text, method_combination[:2], crumbs, error_skip, error_report)

    converter = RomanizationConverter(method_combination)

    converted_words = []

    for chunk in chunks:
        converted_syllables = []
        for syllable in chunk:
            # Convert the syllable based on the specified method combination
            converted_text = converter.convert(syllable.full_syllable)
            capped_text = _apply_caps(converted_text, syllable)
            converted_syllables.append(capped_text)

        # Join syllables back into a word and add it to the result
        converted_words.append("".join(converted_syllables))

    # Join words back into a single string and return the converted text
    return " ".join(converted_words)


def cherry_pick(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = True,
                error_report: bool = False) -> str:
    """
    Converts identified, valid romanized Mandarin without altering invalid text. This is particularly useful for
    converting romanized terms mixed within English text.

    Args:
        text (str): The romanized Mandarin text to be processed.
        method_combination (str): The combination of romanization methods, converting from the first and to the second.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors if a method fails. Defaults to True.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        str: The processed text after applying the best available method from the combination.

    Example:
        >>> text = "Welcome to Zhongguo"
        >>> cherry_pick(text, method_combination="py-wg")
        "Welcome to Chung-kuo"
    """
    stopwords = load_stopwords()
    config, chunks = _setup_and_process(text, method_combination[:2], crumbs, error_skip, error_report)
    converter = RomanizationConverter(method_combination)
    converted_words = []

    def _process_syllables(syllable_list: List[Syllable], convert: bool) -> str:
        """
        Processes the syllables in romanized Mandarin text and applies optional conversions.

        Args:
            syllable_list (List[Syllable]): A list of syllables extracted from the romanized Mandarin text.
            convert (bool): Whether to apply additional conversions (e.g., romanization tweaks).

        Returns:
            str: The processed text with syllables adjusted based on the given configuration.
        """
        return ''.join(
            _apply_caps(converter.convert(syl.full_syllable) if convert else syl.full_syllable, syl)
            for syl in syllable_list
        )

    for chunk in chunks:
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            word = ''.join(syl.full_syllable for syl in chunk).lower()
            if all(syl.valid for syl in chunk) and word not in stopwords:
                converted_words.append(_process_syllables(chunk, convert=True))
            else:
                converted_words.append(_process_syllables(chunk, convert=False))
        else:
            converted_words.append(chunk)

    return "".join(converted_words)


def syllable_count(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False) \
        -> list[int]:
    """
    Returns the count of syllables for each word in the processed text.

    Args:
        text (str): The text to be processed.
        method (str): The method of romanization for the supplied text.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        List[int]: A list of lengths for each valid word in the processed text.

    Example:
        >>> text = "Zhongguo"
        >>> syllable_count(text, method="py")
        [2]
    """
    config, chunks = _setup_and_process(text, method, crumbs, error_skip, error_report)

    return [lengths if all(syllable.valid for syllable in chunk) else 0 for chunk in chunks for lengths in [len(chunk)]]


def detect_method(text: str, per_word: bool = False, crumbs: bool = False, error_skip: bool = False,
                  error_report: bool = False) -> Union[List[str], List[Dict[str, List[str]]]]:
    """
    Detects the romanization method of the given text or individual words.

    Args:
        text (str): The text to be analyzed.
        per_word (bool, optional): Whether to report the possible romanization methods for each word. Defaults to False.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        Union[List[str], List[Dict[str, List[str]]]]: A list of detected methods, either for the full text or per word.

    Example:
        >>> text = "Zhongguo"
        >>> detect_method(text)
        ['py']
    """
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)
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
    Validates the processed text or individual words based on the selected method.

    Args:
        text (str): The text to be validated.
        method (str): The method to apply for validation.
        per_word (bool, optional): Whether to report the validity of the entire text or each word. Defaults to False.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        Union[bool, list[dict]]: Validation results, either as a boolean for the entire text or a detailed list per
        word.

    Example:
        >>> text = "Zhongguo"
        >>> validator(text, method="py")
        True
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
