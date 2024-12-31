import os
import unittest
import subprocess
import sys

# Set the PYTHONPATH to include the directory containing the RoManTools package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from RoManTools.main import main


os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'


class TestMainExecutionFromIDE(unittest.TestCase):

    def test_main_execution_segment(self):
        main(["segment", "-i", "Zhongguo ti'an tianqi", "-m", "py"])

    def test_main_execution_validator(self):
        main(["validator", "-i", "Zhongguo ti'an tianqi", "-m", "py"])

    def test_main_execution_convert_text(self):
        main(["convert", "-i", "Zhongguo ti'an tianqi", "-f", "py", "-t", "wg"])

    def test_main_execution_cherry_pick(self):
        main(["cherry_pick", "-i", "Zhongguo ti'an tianqi", "-f", "py", "-t", "wg"])

    def test_main_execution_syllable_count(self):
        main(["syllable_count", "-i", "Zhongguo ti'an tianqi", "-m", "py"])

    def test_main_execution_detect_method(self):
        main(["detect_method", "-i", "Zhongguo ti'an tianqi"])

    # Test error handling

    def test_main_execution_error_no_action(self):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 2)

    def test_main_execution_no_method_error(self):
        with self.assertRaises(SystemExit) as cm:
            main(["segment", "-i", "Zhongguo ti'an tianqi"])
        self.assertEqual(cm.exception.code, 2)

    def test_main_execution_invalid_method_error(self):
        with self.assertRaises(SystemExit) as cm:
            main(["segment", "-i", "Zhongguo ti'an tianqi", "-m", "ah"])
        self.assertEqual(cm.exception.code, 2)

    def test_main_execution_missing_conversion_parameter_error(self):
        with self.assertRaises(SystemExit) as cm:
            main(["convert", "-i", "Zhongguo ti'an tianqi", "-f", "py"])
        self.assertEqual(cm.exception.code, 2)
