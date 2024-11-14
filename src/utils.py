from typing import Dict, Union, List, Tuple, Set
from .config import Config
from .chunk import TextChunkProcessor
from .syllable import Syllable
from .conversion import RomanizationConverter
from .data_loader import load_method_params, load_stopwords
from functools import lru_cache
# from memory_profiler import profile


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
    if config.crumbs:
        print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, **load_method_params(method, config))
    return processor.get_chunks()


@lru_cache(maxsize=1000)
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


@lru_cache(maxsize=1000000)
def _apply_caps(text: str, syllable: Syllable) -> str:
    """
    Applies capitalization rules based on the syllable's properties.

    Args:
        text (str): The text to be transformed.
        syllable (Syllable): The syllable object containing capitalization rules.

    Returns:
        str: The transformed text with applied capitalization.
    """
    if syllable.uppercase:
        return text.upper()
    elif syllable.capitalize:
        return text.capitalize()
    return text


def _join_syllables(syllable_list: List[Tuple[str, Syllable]], convert_to: str, all_valid: bool,
                    all_but_last_valid: bool, stopwords: Set[str]) -> str:
    vowels = {'a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ'}

    final_word = syllable_list[0][0]
    word = "".join(t[0] for t in syllable_list)
    count_of_syllables = len(syllable_list) + 1 if all_but_last_valid else len(syllable_list)

    if (all_valid or all_but_last_valid) and word.lower() not in stopwords:
        for i in range(1, count_of_syllables):
            if i >= len(syllable_list):
                break

            prev_syllable = syllable_list[i - 1][0]
            curr_syllable = syllable_list[i][0]

            if convert_to == 'py' and syllable_list[i][1].valid:
                if (prev_syllable[-1] in vowels and curr_syllable[0] in vowels) or \
                        (prev_syllable.endswith('er') and curr_syllable[0] in vowels) or \
                        (prev_syllable[-1] == 'n' and curr_syllable[0] in vowels) or \
                        (prev_syllable.endswith('ng') and curr_syllable[0] in vowels):
                    final_word += "'" + curr_syllable
                else:
                    final_word += curr_syllable
            elif convert_to == 'wg':
                final_word += "-" + curr_syllable if syllable_list[i][1].valid else curr_syllable
        return final_word

    return word


@lru_cache(maxsize=1000000)
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


@lru_cache(maxsize=1000000)
def convert_text(text: str, convert_from: str, convert_to: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
    """
    Converts the given text using the specified method combination.

    Args:
        text (str): The text to be converted.
        convert_from (str): The romanization method to convert from.
        convert_to (str): The romanization method to convert to.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors. Defaults to False.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        str: The converted text.

    Example:
        >>> text = "Zhongguo"
        >>> convert_text(text, convert_from="py", convert_to="wg")
        'Chung-kuo'
    """
    config, chunks = _setup_and_process(text, convert_from, crumbs, error_skip, error_report)

    converter = RomanizationConverter(f"{convert_from}_{convert_to}")

    converted_words = []

    for chunk in chunks:
        converted_syllables = []
        for syllable in chunk:
            # Convert the syllable based on the specified method combination
            converted_text = converter.convert(syllable.full_syllable)
            capped_text = _apply_caps(converted_text, syllable)
            converted_syllables.append(capped_text)

        # Join syllables back into a word and add it to the result
        if convert_to == "wg":
            converted_word = "-".join(converted_syllables)
        else:
            converted_word = "".join(converted_syllables)
        converted_words.append(converted_word)

    # Join words back into a single string and return the converted text
    return " ".join(converted_words)


@lru_cache(maxsize=1000000)
def cherry_pick(text: str, convert_from: str, convert_to: str, crumbs: bool = False, error_skip: bool = True,
                error_report: bool = False) -> str:
    """
    Converts identified, valid romanized Mandarin without altering invalid text. This is particularly useful for
    converting romanized terms mixed within English text.

    Args:
        text (str): The romanized Mandarin text to be processed.
        convert_from (str): The romanization method to convert from.
        convert_to (str): The romanization method to convert to.
        crumbs (bool, optional): Whether to display debugging crumbs. Defaults to False.
        error_skip (bool, optional): Whether to skip errors if a method fails. Defaults to True.
        error_report (bool, optional): Whether to report errors. Defaults to False.

    Returns:
        str: The processed text after applying the best available method from the combination.

    Example:
        >>> text = "Welcome to Zhongguo!"
        >>> cherry_pick(text, convert_from="py", convert_to="wg")
        "Welcome to Chung-kuo!"
    """
    config, chunks = _setup_and_process(text, convert_from, crumbs, error_skip, error_report)
    stopwords = set(load_stopwords())
    unsupported_contractions = {"t", "m"}
    supported_contractions = {"s", "d", "ll"}

    def get_prefix(syl: Syllable) -> str:
        return ("'" if syl.has_apostrophe else "") + ("-" if syl.has_dash else "")

    def return_caps_and_symbols(syllable_list: list[Tuple[str, Syllable]]) -> str:

        all_valid = all(syl[1].valid for syl in syllable_list)
        all_but_last_valid = all(syl[1].valid for syl in syllable_list[:-1]) and (syllable_list[-1][1].has_apostrophe and syllable_list[-1][1].full_syllable in supported_contractions)

        for i, (syllable, syl) in enumerate(syllable_list):
            capped_text = _apply_caps(syllable, syl)
            if (syl.has_apostrophe and
                    (syl.full_syllable in supported_contractions or syl.full_syllable in unsupported_contractions)):
                syllable_list[i] = (f"'{capped_text}", syl)
            elif syl.has_dash:
                syllable_list[i] = (f"-{capped_text}", syl)
            else:
                syllable_list[i] = (capped_text, syl)

        return _join_syllables(syllable_list, convert_to, all_valid, all_but_last_valid, stopwords)


    def convert_word(chunk_word: list[Syllable]) -> list[Tuple[str, Syllable]]:
        converter = RomanizationConverter(f"{convert_from}_{convert_to}")
        collected_conversions = []

        all_valid = all(syl.valid for syl in chunk_word)
        all_but_last_valid = all(syl.valid for syl in chunk_word[:-1]) and chunk_word[-1].full_syllable in supported_contractions and chunk_word[-1].has_apostrophe

        if all_valid or all_but_last_valid:
            for syl in chunk_word:
                if syl.valid:
                    converted_syllable = converter.convert(syl.full_syllable)
                    collected_conversions.append((converted_syllable, syl))
                else:
                    collected_conversions.append((syl.full_syllable, syl))
        else:
            collected_conversions = [(syl.full_syllable, syl) for syl in chunk_word]

        return collected_conversions

    concat_text = []
    for chunk in chunks:
        if isinstance(chunk, list) and all(isinstance(syl, Syllable) for syl in chunk):
            word = ''.join(get_prefix(syl) + syl.full_syllable for syl in chunk)
            last_syllable = chunk[-1]
            if word not in stopwords or (
                    last_syllable.has_apostrophe and last_syllable.full_syllable not in unsupported_contractions):
                processed_word = convert_word(chunk)
            else:
                processed_word = [(syl.full_syllable, syl) for syl in chunk]
            concat_text.append(return_caps_and_symbols(processed_word))

        else:
            concat_text.append(chunk)

    return "".join(concat_text)

@lru_cache(maxsize=1000000)
# @profile
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


@lru_cache(maxsize=1000000)
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


@lru_cache(maxsize=1000000)
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
