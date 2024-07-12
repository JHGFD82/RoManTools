# utils.py

import re
import os
from .syllable import Syllable, find_initial, find_final
from .conversion import convert_romanization
from .data_loader import load_romanization_data, load_stopwords
base_path = os.path.dirname(__file__)


def get_method_params(method):
    method = 'pinyinDF' if method == 'PY' else 'wadegilesDF'
    init_list, fin_list, ar = load_romanization_data(os.path.join(base_path, 'data', f'{method}.csv'))
    return {
        'method': method,
        'init_list': init_list,
        'fin_list': fin_list,
        'ar': ar
    }


def split_text_into_chunks(text, cherry_pick):
    try:
        if cherry_pick:
            return re.findall(r'\'s[^a-zA-Z]|\'t[^a-zA-Z]|[\w]+|[^a-zA-Z]+', text)
        else:
            return text.split()
    except ValueError:
        return []


def analyze_chunk(chunk, method_params, words, crumbs):
    syls = []
    more_text = True
    next_syl_start = 0
    syl_index = -1
    error_found = ''
    is_cap = True if chunk[0].isupper() else False
    chunk = chunk.lower()

    while more_text and not error_found:
        syl_index += 1
        syl_parts = dict(method_params)

        syl_parts.update(find_initial(chunk[next_syl_start:], **syl_parts))
        initial_len = 0 if syl_parts['initial'] == 'ø' else len(syl_parts['initial'])

        if 'error' in syl_parts:
            syl_parts.update({'final': ''})
            final_len = 0
            error_found = syl_parts['error']
        else:
            syl_parts.update(find_final(chunk[next_syl_start + initial_len:], **syl_parts))
            final_len = len(syl_parts['final'])

        syls.append(Syllable(**syl_parts))

        if is_cap and syl_index < 1:
            syls[syl_index].cap = True

        next_syl_start += initial_len + final_len

        if not syls[syl_index].valid:
            if not error_found:
                error_found = 'invalid syllable: ' + syls[syl_index].full_syl
            if len(chunk[next_syl_start:]) > 0:
                syl_parts.update({'initial': chunk[next_syl_start:], 'final': ''})
                syls.append(Syllable(**syl_parts))
        else:
            if len(chunk[next_syl_start:]) < 1:
                more_text = False

    words.append(syls)

    if crumbs:
        for syl in syls:
            print(syl.initial + ' [initial]' + '\n' +
                  syl.initial + '|' + syl.final + ' [final]' + '\n' +
                  syl.full_syl + ' valid: ' + str(syl.valid))
        (print(chunk + ' syllable count: ' + str(len(syls)))
         if not error_found else print(error_found))
        print('-----------')

    return syls, error_found, words


def syllable_count(text, skip_count=False, method='PY', method_report=False,
                   crumbs=False, error_skip=False, error_report=False,
                   convert='', cherry_pick=False):

    print('# Analyzing ' + text + ' #') if crumbs else ''

    method_params = get_method_params(method)
    result = []
    words = []
    error_collect = []

    chunks = split_text_into_chunks(text, cherry_pick)

    for chunk in chunks:
        syls, error_found, words = analyze_chunk(chunk, method_params, words, crumbs)

        if error_found and not error_skip:
            return [0]
        elif error_found and error_report:
            error_collect.append(error_found)

    if not skip_count:
        result.append([len(w) for w in words if all(s.valid for s in w)])

    if error_report and error_collect:
        result.append(error_collect)

    if method_report:
        result.append('Pinyin' if method == 'PY' else 'Wade-Giles')

    stopwords = load_stopwords(os.path.join(base_path, 'data', 'stopwords.txt'))

    if convert:
        converted_string = ''
        for word in words:
            adjusted_word = ''.join(syl.full_syl for syl in word)
            valid_word = all(syl.valid for syl in word)
            if valid_word and adjusted_word not in stopwords:
                adjusted_word = ('-'.join(convert_romanization(syl.full_syl, convert)
                                          for syl in word))
            converted_string += (adjusted_word.capitalize()
                                 if 'cap' in word[0].__dict__ else adjusted_word)

        result.append(converted_string.strip())

    return result
