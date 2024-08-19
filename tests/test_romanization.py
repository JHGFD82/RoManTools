# tests/test_romanization.py

import unittest
from Tools.utils import convert_text, segment_text, syllable_count
from io import StringIO
from unittest.mock import patch


class TestRomanization(unittest.TestCase):

    def test_convert_text(self):
        result = convert_text('ni hao chang\'an yuan', method_combination='py_wg')
        self.assertEqual(result, 'ni hao ch’angan yüan')

    def test_segment_text(self):
        result = segment_text('ni hao chang\'an yuan')
        self.assertEqual(result, ['ni', 'hao', ['chang', 'an'], 'yuan'])

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
