# tests/test_romanization.py

import unittest
from Tools.utils import convert_text, segment_text, syllable_count
from io import StringIO
from unittest.mock import patch


class TestRomanization(unittest.TestCase):

    # PINYIN CHUNK GENERATION TESTING #
    def test_segment_text_basic_valid_syllable_vowel(self):
        result = segment_text('a, e, o, ai, ou', method='PY')
        self.assertEqual(result, [['a'], ['e'], ['o'], ['ai'], ['ou']])

    def test_segment_text_basic_valid_syllable_initial(self):
        result = segment_text('ba gu zhi ying kai lou yan', method='PY')
        self.assertEqual(result, [['ba'], ['gu'], ['zhi'], ['ying'], ['kai'], ['lou'], ['yan']])

    def test_segment_text_complex_finals_er_n_ng(self):
        result = segment_text('han xiang ran ling er', method='PY')
        self.assertEqual(result,  [['han'], ['xiang'], ['ran'], ['ling'], ['er']])

    def test_segment_text_complex_edge_cases(self):
        result = segment_text('chen chong zhen', method='PY')
        self.assertEqual(result,  [['chen'], ['chong'], ['zhen']])

    def test_segment_text_multi_syllable_no_apostrophe(self):
        result = segment_text('xiaoming changan wenxin liangxiao', method='PY')
        self.assertEqual(result, [['xiao', 'ming'], ['chan', 'gan'], ['wen', 'xin'], ['liang', 'xiao']])

    def test_segment_text_multi_syllable_apostrophe(self):
        result = segment_text("chang'an shan'er li'an", method='PY')
        self.assertEqual(result, [['chang', 'an'], ['shan', 'er'], ['li', 'an']])

    def test_segment_text_invalid_initials(self):
        result = segment_text('xa qo vei', method='PY')
        self.assertEqual(result, [['xa'], ['qo'], ['vei']])

    def test_segment_text_invalid_finals(self):
        result = segment_text('banp zhirr mingk', method='PY')
        self.assertEqual(result, [['ban', 'p'], ['zhi', 'rr'], ['ming', 'k']])

    def test_segment_text_special_cases_er_n_ng(self):
        result = segment_text('sheng deng er han shier', method='PY')
        self.assertEqual(result, [['sheng'], ['deng'], ['er'], ['han'], ['shi', 'er']])

    def test_segment_text_special_cases_combined_initials(self):
        result = segment_text('shuang huang shun', method='PY')
        self.assertEqual(result, [['shuang'], ['huang'], ['shun']])

    def test_segment_text_edge_cases_ambiguous_finals(self):
        result = segment_text('wenti linping gangzhi', method='PY')
        self.assertEqual(result, [['wen', 'ti'], ['lin', 'ping'], ['gang', 'zhi']])

    def test_segment_text_no_valid_finals(self):
        result = segment_text('blar ziang shoing', method='PY')
        self.assertEqual(result, [['blar'], ['ziang'], ['shoing']])

    def test_segment_text_multi_vowel_combinations(self):
        result = segment_text('ai ei ou uan ie', method='PY')
        self.assertEqual(result, [['ai'], ['ei'], ['ou'], ['uan'], ['ie']])

    def test_segment_text_one_syllable_edge_case(self):
        result = segment_text('a e ou yi', method='PY')
        self.assertEqual(result, [['a'], ['e'], ['ou'], ['yi']])

    def test_segment_text_multi_syllable_edge_case_er_n_ng(self):
        result = segment_text('zhuangyuan wenxiang gangren', method='PY')
        self.assertEqual(result, [['zhuang', 'yuan'], ['wen', 'xiang'], ['gang', 'ren']])

    # ROMANIZATON CONVERSION TESTING #
    def test_convert_text(self):
        result = convert_text('ni hao chang\'an yuan', method_combination='py_wg')
        self.assertEqual(result, 'ni hao ch’angan yüan')

    def test_segment_text(self):
        result = segment_text('ni hao chang\'an yuan')
        self.assertEqual(result, ['ni', 'hao', ['chang', 'an'], 'yuan'])

    # SYLLABLE_COUNT TESTING #
    def test_syllable_count(self):
        result = syllable_count('ni hao', method='PY')
        self.assertEqual(result, [1, 1])

    def test_syllable_count_multi(self):
        result = syllable_count('chang\'an yuan', method='PY')
        self.assertEqual(result, [2, 1])

    @patch('sys.stdout', new_callable=StringIO)
    def test_syllable_count_output(self, mock_stdout):
        syllable_count('ni hao', method='PY', crumbs=True)
        expected_output = ('# Analyzing ni hao #\n'
                           '# PY romanization data loaded #\n'
                           'n [initial]\n'
                           'n|i [final]\n'
                           'ni valid: True\n'
                           'ni syllable count: 1\n'
                           '-----------\n'
                           'h [initial]\n'
                           'h|ao [final]\n'
                           'hao valid: True\n'
                           'hao syllable count: 1\n'
                           '-----------\n')
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_syllable_count_half_output(self, mock_stdout):
        syllable_count('ni haa', method='PY', crumbs=True)
        expected_output = ('# Analyzing ni haa #\n'
                           '# PY romanization data loaded #\n'
                           'n [initial]\n'
                           'n|i [final]\n'
                           'ni valid: True\n'
                           'ni syllable count: 1\n'
                           '-----------\n'
                           'h [initial]\n'
                           'h|aa [final]\n'
                           'haa valid: False\n'
                           'haa syllable count: 0\n'
                           '-----------\n')
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_syllable_count_failed_output(self, mock_stdout):
        syllable_count('noi haa', method='PY', crumbs=True)
        expected_output = ('# Analyzing noi haa #\n'
                           '# PY romanization data loaded #\n'
                           'n [initial]\n'
                           'n|oi [final]\n'
                           'noi valid: False\n'
                           'noi syllable count: 0\n'
                           '-----------\n'
                           'h [initial]\n'
                           'h|aa [final]\n'
                           'haa valid: False\n'
                           'haa syllable count: 0\n'
                           '-----------\n')
        self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
