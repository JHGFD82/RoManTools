# utils.py
from __future__ import annotations

import re
import os

from .syllable import Syllable, find_initial, find_final
from .conversion import RomanizationConverter
from .data_loader import load_romanization_data, load_stopwords

base_path = os.path.dirname(__file__)


def get_method_params(method: str) -> dict:
    method = 'pinyinDF' if method == 'PY' else 'wadegilesDF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method}.csv'))
    return {
        'method': method,
        'init_list': init_list,
        'fin_list': fin_list,
        'ar': ar
    }


def split_text_into_chunks(text: str, cherry_pick: bool = False) -> list:
    try:
        if cherry_pick:
            return re.findall(r'\'s[^a-zA-Z]|\'t[^a-zA-Z]|\w+|[^a-zA-Z]+', text)
        else:
            return text.split()
    except ValueError:
        return []


def analyze_chunk(chunk: str, method_params: dict, words: list, crumbs: bool) -> tuple[list[Syllable], str, list]:
    syls = []
    next_syl_start = 0
    chunk = chunk.lower()

    while True:
        next_syl_start, syl_parts, error_found = _get_next_syllable(chunk, next_syl_start, method_params)

        if error_found:
            break

        syls.append(Syllable(**syl_parts))

        if next_syl_start >= len(chunk):
            break

    words.append(syls)

    if crumbs:
        _print_crumbs(syls, chunk, error_found)

    return syls, error_found, words


# new private function to handle getting the next syllable details
def _get_next_syllable(chunk, next_syl_start, method_params):
    syl_parts = dict(method_params)
    syl_parts.update(find_initial(chunk[next_syl_start:], **syl_parts))
    initial_len = 0 if syl_parts['initial'] == 'ø' else len(syl_parts['initial'])
    error_found = ''

    if 'error' in syl_parts:
        syl_parts.update({'final': ''})
        error_found = syl_parts['error']
    else:
        syl_parts.update(find_final(chunk[next_syl_start + initial_len:], **syl_parts))
    next_syl_start += initial_len + len(syl_parts['final'])
    return next_syl_start, syl_parts, error_found


# new private function to handle the logging of 'crumbs'
def _print_crumbs(syls, chunk, error_found):
    for syl in syls:
        print(syl.initial + ' [initial]' + '\n' +
              syl.initial + '|' + syl.final + ' [final]' + '\n' +
              syl.full_syl + ' valid: ' + str(syl.valid))
    (print(chunk + ' syllable count: ' + str(len(syls)))
     if not error_found else print(error_found))
    print('-----------')


def syllable_count(text, skip_count=False, method='PY', method_report=False, crumbs=False,
                   error_skip=False, error_report=False, convert='', cherry_pick=False):
    if crumbs:
        print(f'# Analyzing {text} #')

    method_params = get_method_params(method)

    words, error_collect = process_chunks(text, method_params, cherry_pick, error_skip, error_report, crumbs)

    result = compile_results(words, error_collect, method, skip_count, method_report, error_report)

    if convert:
        converter = RomanizationConverter()  # Initialize only when needed
        result.append(convert_words(words, convert, converter))

    return result


def process_chunks(text, method_params, cherry_pick, error_skip, error_report, crumbs):
    chunks = split_text_into_chunks(text, cherry_pick)
    words = []
    error_collect = []

    for chunk in chunks:
        syls, error_found, words = analyze_chunk(chunk, method_params, words, crumbs)

        if error_found:
            if not error_skip:
                return [], [0]
            if error_report:
                error_collect.append(error_found)

    return words, error_collect


def compile_results(words, error_collect, method, skip_count, method_report, error_report):
    result = []

    if not skip_count:
        result.append([len(w) for w in words if all(s.valid for s in w)])

    if error_report and error_collect:
        result.append(error_collect)

    if method_report:
        result.append('Pinyin' if method == 'PY' else 'Wade-Giles')

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

        converted_string += adjusted_word

    return converted_string.strip()
