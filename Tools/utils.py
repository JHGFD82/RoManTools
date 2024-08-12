# utils.py
from __future__ import annotations

import re
import os

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
    def __init__(self, text):
        self.text = text
        self.chunks = []
        self.process_chunks()  # Automatically process chunks upon initialization

    @staticmethod
    def split_pinyin_word(word):
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

    def get_chunks(self):
        return self.chunks


def get_method_params(method: str) -> dict:
    method = 'pinyinDF' if method == 'PY' else 'wadegilesDF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method}.csv'))
    if config and config.crumbs:
        print(f"# {str.upper(method)} romanization data loaded #")
    return {
        'init_list': init_list,
        'fin_list': fin_list,
        'ar': ar
    }


# new private function to handle the logging of 'crumbs'
def _print_crumbs(syls, chunk, error_found):
    for syl in syls:
        print(syl.initial + ' [initial]' + '\n' +
              syl.initial + '|' + syl.final + ' [final]' + '\n' +
              syl.full_syl + ' valid: ' + str(syl.valid))
    (print(chunk + ' syllable count: ' + str(len(syls)))
     if not error_found else print(error_found))
    print('-----------')
    config = Config(crumbs=crumbs, error_skip=error_skip, error_report=error_report)

    if config.crumbs:
        print(f'# Analyzing {text} #')

    method_params = get_method_params(method, config)

    processor = TextChunkProcessor(text)
    chunks = processor.get_chunks()

    result = count_syllables_in_text(chunks, config, **method_params)

    return result


def count_syllables_in_text(chunks, init_list, fin_list, ar):

    # Map chunks to syllables and validate them
    result = []
    for chunk in chunks:
        if isinstance(chunk, list):  # Multi-syllable word
            words = []
            for syllable in chunk:
                # Create a Syllable object
                syllable_obj = Syllable(syllable, ar=ar, init_list=init_list, fin_list=fin_list)
                words.append(syllable_obj)
            # Check if all syllables are valid and count them
            if all(s.valid for s in words):
                result.append(len(words))
            else:
                result.append(0)  # Or handle invalid syllables as needed
        else:  # Single-syllable word
            syllable_obj = Syllable(chunk, ar=ar, init_list=init_list, fin_list=fin_list)

            if syllable_obj.valid:
                result.append(1)
            else:
                result.append(0)  # Or handle invalid syllables as needed

    return result


def convert_words(words, convert, converter):
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
