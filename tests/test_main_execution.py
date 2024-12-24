import os
import unittest
import subprocess
import sys
from main import main


os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

class TestMainExecutionFromIDE(unittest.TestCase):

    def test_main_execution(self):
        main(["segment", "-i", "Zhongguo ti'an tianqi", "-m", "py"])


class TestMainExecutionFromCLI(unittest.TestCase):

    def test_main_execution(self):
        result = subprocess.run([sys.executable, '../RoManTools/main.py', 'segment', '-i', 'Zhongguo ti\'an tianqi',
                                 '-m', 'py'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("[['zhong', 'guo'], ['ti', 'an'], ['tian', 'qi']]", result.stdout)
