# utils.py

import re
from .syllable import Syllable, find_initial, find_final
from .conversion import convert_romanization

def syllable_count(text, skip_count=False, method='PY', method_report=False,
                   crumbs=False, error_skip=False, error_report=False,
                   convert='', cherry_pick=False):
    print('# Analyzing ' + text + ' #') if crumbs else ''

    try:
        if cherry_pick:
            chunks = re.findall(r'\'s[^a-zA-Z]|\'t[^a-zA-Z]|[\w]+|[^a-zA-Z]+', text)
        else:
            chunks = text.split()
    except ValueError:
        return [0]

    method_values = {'PY': ('PY', PY_init_list, PY_fin_list, PY_ar),
                     'WG': ('WG', WG_init_list, WG_fin_list, WG_ar)}
    method_params = dict(zip(['method', 'init_list', 'fin_list', 'ar'], method_values[method]))

    result = []
    words = []
    error_collect = []

    for chunk in chunks:
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
