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
    def __init__(self, text: str, config: Config, ar: np.ndarray, init_list: List[str], fin_list: List[str],
                 method: str):
        self.text = text
        self.config = config
        self.ar = ar
        self.init_list = init_list
        self.fin_list = fin_list
        self.method = method
        self.chunks = []
        self.process_chunks()

    def process_chunks(self):
        words = re.findall(r"[a-zA-ZüÜ]+(?:['’ʼ`\-–—][a-zA-ZüÜ]+)?", self.text)

        for word in words:
            split_words = self.split_pinyin_word(word)
            self._process_split_words(split_words)

    def _process_split_words(self, split_words: Union[str, List[str]]):
        syllables = []

        if isinstance(split_words, list):
            for i, part in enumerate(split_words):
                remainder = split_words[i + 1] if i < len(split_words) - 1 else ""
                syllables.append(Syllable(part, self.config, self.ar, self.init_list, self.fin_list, remainder))
        else:
            remaining_text = split_words
            while remaining_text:
                syllable_obj = Syllable(remaining_text, self.config, self.ar, self.init_list, self.fin_list)
                syllables.append(syllable_obj)
                remaining_text = syllable_obj.remainder
                if not syllable_obj.remainder:
                    break

        self.chunks.append(syllables)

    @staticmethod
    def split_word(self, word: str) -> List[str]:
        if self.method == "wg":
            # For Wade-Giles, split words using hyphens (including en-dash and em-dash)
            split_words = re.split(r"[\-–—]", word)
        else:
            # For Pinyin or other systems, split on a broader range of delimiters
            split_words = re.split(r"[‘’'ʼ`\-–—]", word)

    def get_chunks(self) -> List[Union[str, List[Syllable]]]:
        return self.chunks


def get_method_params(method: str, config: Config) -> Dict[str, Union[List[str], np.ndarray]]:
    method_file = f'{method.lower()}DF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method_file}.csv'))

    if config.crumbs:
        print(f"# {method.upper()} romanization data loaded #")

    return {
        'ar': ar,
        'init_list': init_list,
        'fin_list': fin_list
    }


def process_text(text: str, method: str, config: Config) -> List[Union[List[Syllable], Syllable]]:
    if config.crumbs:
        print(f'# Analyzing {text} #')
    processor = TextChunkProcessor(text, config, **get_method_params(method, config))
    return processor.get_chunks()


def segment_text(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False)\
        -> List[Union[List[Syllable], Syllable]]:
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    chunks = process_text(text, method, config)

    return [[chunk.full_syllable for chunk in chunks] for chunks in chunks]


def convert_text(text: str, method_combination: str, crumbs: bool = False, error_skip: bool = False,
                 error_report: bool = False) -> str:
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    chunks = process_text(text, method_combination[:2], config)
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


def syllable_count(text: str, method: str, crumbs: bool = False, error_skip: bool = False, error_report: bool = False)\
        -> list[int]:
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    chunks = process_text(text, method, config)

    return [lengths if all(syllable.valid for syllable in chunk) else 0 for chunk in chunks for lengths in [len(chunk)]]
