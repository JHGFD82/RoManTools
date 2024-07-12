# tests/test_romanization.py

import unittest
from romanization import syllable_count, convert_romanization

class TestRomanization(unittest.TestCase):
    def test_syllable_count(self):
        result = syllable_count('ni hao', method='PY')
        self.assertEqual(result, [[2]])

    def test_convert_romanization(self):
        result = convert_romanization('ni', 'PYWG')
        self.assertEqual(result, 'ni4')

if __name__ == '__main__':
    unittest.main()
