# tests/test_romanization.py

import unittest
from Tools import syllable_count, convert_romanization


class TestRomanization(unittest.TestCase):
    def test_syllable_count(self):
        result = syllable_count('ni hao', method='PY')
        self.assertEqual(result, [[1, 1]])

    def test_convert_romanization(self):
        result = convert_romanization('hao', 'PYWG')
        self.assertEqual(result, 'hao')


if __name__ == '__main__':
    unittest.main()
