# utils.py
import re
import os
from typing import Dict, Union, List
import numpy as np
from .syllable import Syllable
from .conversion import RomanizationConverter
from .data_loader import load_romanization_data, load_stopwords

base_path = os.path.dirname(__file__)


class Config:
    def __init__(self, crumbs: bool = False, error_skip: bool = False, error_report: bool = False):
        self.crumbs = crumbs
        self.error_skip = error_skip
        self.error_report = error_report


class TextChunkProcessor:
    def __init__(self, text: str):
        self.text = text
        self.chunks = []
        self.process_chunks()  # Automatically process chunks upon initialization

    @staticmethod
    def split_pinyin_word(word: str) -> Union[List[str], str]:
        # Split word based on apostrophes or dashes
        if re.search(r"[‘’'ʼ`\-–—]", word):  # Escape the hyphen here with a backslash
            # Split the word at apostrophes or dashes
            syllables = re.split(r"[‘’'ʼ`\-–—]", word)
            return [syllable for syllable in syllables if syllable]  # Return list, removing any empty strings
        else:
            # If no split is needed, return the word as a string
            return word

    def process_chunks(self):
        # Find all words, including those separated by apostrophes or dashes
        pattern = r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)?"
        words = re.findall(pattern, self.text)

        # Process each word to either split or return as is
        for word in words:
            chunk = self.split_pinyin_word(word)
            self.chunks.append(chunk)

    def get_chunks(self) -> Union[List[str], str]:
        return self.chunks


def get_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
    method_file = f'{method.lower()}DF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method_file}.csv'))

    if config.crumbs:
        print(f"# {method.upper()} romanization data loaded #")

    return {
        'init_list': init_list,
        'fin_list': fin_list,
        'ar': ar
    }


def process_text(text: str, config: Config) -> List[Union[List[str], str]]:
    processor = TextChunkProcessor(text)
    if config.crumbs:
        print(f'# Analyzing {text} #')
    return processor.get_chunks()


def convert_text(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    chunks = process_text(text, config)
    converter = RomanizationConverter(method_combination)

    result = ' '.join(
        ''.join(converter.convert(syllable) for syllable in chunk) if isinstance(chunk, list)
        else converter.convert(chunk)
        for chunk in chunks
    )

    return result.strip()


def cherry_pick(words: List, convert, converter):
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


def segment_text(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False)\
        -> List[Union[List[Syllable], Syllable]]:
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    chunks = process_text(text, method, config)

    return [chunk.full_syllable if isinstance(chunk, Syllable) else [syllable.full_syllable for syllable in chunk]
            for chunk in chunks]


def count_syllables_in_text(chunks: list, config: Config, init_list: List[str], fin_list: List[str], ar: np.ndarray)\
        -> list[int]:
    def process_syllables(syllables: list) -> int:
        """Process a list of syllables, validate them, and handle crumbs."""
        for syllable in syllables:
            syllable_obj = Syllable(syllable, config, ar=ar, init_list=init_list, fin_list=fin_list)
            if config.crumbs:
                print(f"{syllable_obj.full_syl} valid: {syllable_obj.valid}")
            syllable_objects.append(syllable_obj)

        if all(s.valid for s in syllable_objects):
            return len(syllable_objects)
        return 0

    def handle_crumbs(word: str, count: int):
        """Handle crumbs output for multi-syllable words."""
        if config.crumbs:
            print(f"{word} syllable count: {count}")
            print('-----------')

    result = []
    for chunk in chunks:
        syllable_objects = []

        if isinstance(chunk, list):  # Multi-syllable word
            full_word = ''.join(chunk)
            syllables_count = process_syllables(chunk)
            result.append(syllables_count)
            handle_crumbs(full_word, syllables_count)

        else:  # Single-syllable word
            syllables_count = process_syllables([chunk])
            result.append(syllables_count)
            handle_crumbs(chunk, syllables_count)

    return result
