# PACKAGE DEPENDENCIES
import csv
import re
import numpy as np

# REFERENCE DATA
# List of Pinyin initials, finals
PY = np.genfromtxt('data/pinyinDF.csv', delimiter=',', dtype=str)
PY_init_list = list(PY[1:, 0])
PY_fin_list = list(PY[0, 1:])

# List of Wade-Giles initials, finals
WG = np.genfromtxt('data/wadegilesDF.csv', delimiter=',', dtype=str)
WG_init_list = list(WG[1:, 0])
WG_fin_list = list(WG[0, 1:])

# Import Numpy arrays from CSV
PY_ar = PY[1:, 1:] == '1'
WG_ar = WG[1:, 1:] == '1'

# Import stopwords from text file (stopword-generation process detailed in section 5)
with open('data/stopwords.txt', 'r') as f:
    stopwords = f.read().splitlines()

# REFERENCE VARIABLES
# Vowel List
vowel = ['a', 'e', 'i', 'o',
         'u', 'ü', 'v', 'ê', 'ŭ']  # for detecting switch from initial to final

# Dictionary for replacing known invalid characters
symbol_replacements = {'—': '-', '–': '-', '\'': '’', '`': '’',
                       '\u3000': ' '}


# SYLLABLE PART FUNCTIONS
# INITIALS #
def find_initial(text, **kwargs):
    """Identify the initial of the syllable."""

    initial = ''
    result = {}

    for i, c in enumerate(text):

        if c in vowel:
            if i == 0:  # a syllable starts with a vowel
                result.update({'initial': 'ø'})
            else:
                initial = text[:i]
                if initial not in kwargs['init_list']:  # an invalid initial
                    result.update(
                        {'initial': initial, 'error': initial + ': invalid initial'})
                else:
                    result.update({'initial': initial})
            return result

    if not initial:
        result.update({'initial': text, 'error': text + ': no final'})
        return result


# FINALS
def find_final(text, **kwargs):
    """Identify the final of the syllable."""

    result = {}

    for i, c in enumerate(text):

        # ending vowel
        if c in vowel and i + 1 == len(text):
            result.update({'final': text})
            return result

        # if more than one vowel, detect invalid multi-vowel, check if valid syllable
        elif c in vowel and i > 0:
            test_syls = []
            for f_item in list(l for l in kwargs['fin_list'] if l.startswith(text[:i + 1])):
                kwargs.update({'final': f_item})
                test_syls.append(Syllable(**kwargs).valid)
            if True not in test_syls:
                result.update({'final': text[:i]})
                return result

        # consonant
        elif c not in vowel:

            # EXCEPTIONS
            # reference variable to identify end of text
            remainder = len(text) - i - 1

            # er, erh #
            # if syllable before "er", return it, else return "er"
            if (text[i - 1:i + 1] == 'er' and
                    (not remainder or text[i + 1] not in vowel)):
                final = text[:-2] if len(text[:i]) > 1 else text[:i - 1]

            # n, ng #
            elif c == 'n':
                # if there's potential text for final or an invalid "n" final, return "ng", else return "n"
                if remainder and text[i + 1] == 'g':
                    kwargs.update({'final': text[:i + 1]})
                    final = text[:i + 2] if (remainder < 2 or text[i + 2] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i + 1]

                # if there's potential text for final or an invalid final without "n", return "n"
                else:
                    kwargs.update({'final': text[:i]})
                    final = text[:i + 1] if (not remainder or text[i + 1] not in vowel or
                                             not Syllable(**kwargs).valid) else text[:i]

            # stop at all other consonants
            else:
                final = text[:i]

            result.update({'final': final})
            return result


# CONVERSION FUNCTION
def convert_romanization(text, method):
    """Convert given text using provided method in parameters."""

    # VALIDATION #
    # Make sure one of the acceptable methods is supplied
    accepted_methods = ['PYWG', 'WGPY']

    if method not in accepted_methods:
        return text + '(!)'

    source_file = 'data/' + f'{method}.csv'

    with open(source_file) as file:
        r = csv.reader(file)
        convert_dict = {rows[0]: rows[1] for rows in r}
    converted = convert_dict[text]

    return converted


# SYLLABLE CLASS
class Syllable:
    """Properties of an initial/final pair."""

    def __init__(self, initial, final, init_list, fin_list, ar):

        # BASIC INFORMATION
        self.initial = initial
        self.final = final
        self.full_syl = (self.initial + self.final if self.initial[0] != 'ø'
                         else self.initial[1:] + self.final)
        self.length = len(self.full_syl)
        self.valid = self.validate_syllable(init_list, fin_list, ar)

        # SYLLABLE VALIDATION
    def validate_syllable(self, init_list, fin_list, ar):
        try:
            result = ar[
                init_list.index(self.initial),
                fin_list.index(self.final)]
        except ValueError:
            return False
        else:
            return result


def process_chunks(chunks, method, crumbs, error_collect):
    result = []
    words = []
    if method == 'PY':
        method_values = ['PY', PY_init_list, PY_fin_list, PY_ar]
    else:
        method_values = ['WG', WG_init_list, WG_fin_list, WG_ar]

    method_params = dict(zip(['method', 'init_list', 'fin_list', 'ar'], method_values))

    result = []
    words = []
    error_collect = []

    for chunk in chunks:

        # FUNCTION VARIABLES
        syls = []
        more_text = True
        next_syl_start = 0
        syl_index = -1
        error_found = ''
        is_cap = True if chunk[0].isupper() else False
        chunk = chunk.lower()

        # WORD EVALUATION: MAIN FUNCTION
        while more_text and not error_found:

            syl_index += 1
            syl_parts = dict(method_params)

            # Find initial from chunk
            syl_parts.update(find_initial(chunk[next_syl_start:], **syl_parts))
            initial_len = 0 if syl_parts['initial'] == 'ø' else len(syl_parts['initial'])

            # Errors set up false final, otherwise real final is found from chunk
            if 'error' in syl_parts:
                syl_parts.update({'final': ''})
                final_len = 0
                error_found = syl_parts['error']
            else:
                syl_parts.update(find_final(chunk[next_syl_start + initial_len:], **syl_parts))
                final_len = len(syl_parts['final'])

            # Append syllable list with syllable object using found parts
            syls.append(Syllable(**syl_parts))

            # Set capitalization attribute for first syllable
            if is_cap and syl_index < 1:
                syls[syl_index].cap = True

            # Set next syl starting point for reference
            next_syl_start += initial_len + final_len

            # If syllable not valid, set correct error message, set remaining text to new syllable,
            # otherwise check if there is more text
            if not syls[syl_index].valid:
                if not error_found:
                    error_found = 'invalid syllable: ' + syls[syl_index].full_syl
                if len(chunk[next_syl_start:]) > 0:
                    syl_parts.update({'initial': chunk[next_syl_start:], 'final': ''})
                    syls.append(Syllable(**syl_parts))
            else:
                if len(chunk[next_syl_start:]) < 1:
                    more_text = False

        # Append syllable list to word list
        words.append(syls)

        # REPORTING/ERRORS
        # Print all processing steps and errors, return 0 if skipping parameter not set
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

    # DELIVERING RESULTS
    # Syllable Count
    if not skip_count:
        result.append([len(w) for w in words if all(s.valid for s in w)])

    if error_report and error_collect:
        result.append(error_collect)

    if method_report:
        if method == 'PY':
            result.append('Pinyin')
        else:
            result.append('Wade-Giles')

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


# SYLLABLE COUNTER FUNCTION

def syllable_count(text, skip_count=False, method='PY', method_report=False,
                   crumbs=False, error_skip=False, error_report=False,
                   convert='', cherry_pick=False):
    """Produce the count of syllables from any given romanized Chinese text.
    ----------------
    Parameters allowed for additional features:
    * skip_count = "True" to exclude the whole point of this function (no, seriously)
    * method = "PY" (pinyin) as default, but "WG" (Wade-Giles) also supported
    * method_report = "True" to include romanization method in output
    * crumbs = "True" to include step-by-step analysis in output
    * error_skip = "True" to not abort function on invalid text and instead skip to next word
    * error_report = "True" to include error messages in output
    * convert = "PYWG" using from-to structure, "WGPY" also supported
    * cherry_pick = "PYWG" or "WGPY" to convert only identified, valid syllables
        (best for converting paragraphs with multiple languages)"""

    print('# Analyzing ' + text + ' #') if crumbs else ''
    try:
        if cherry_pick:
            chunks = re.findall(r'\'s[^a-zA-Z]|\'t[^a-zA-Z]|\w+|[^a-zA-Z]+', text)
        else:
            chunks = text.split()
    except ValueError:
        return [0]

    error_collect = []
    result = process_chunks(chunks, method, crumbs, error_collect)
    return result

syllable_count(input('Enter your text: '))
