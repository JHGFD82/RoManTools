__version__ = '1.0.0'
"""
RoManTools

This package provides tools for processing romanized Mandarin text, including segmentation, validation, conversion, and
syllable counting. It currently supports romanization methods Pinyin and Wade-Giles.

Modules:
    utils: Utility functions for text segmentation, validation, conversion, and syllable counting.

Functions:
    segment_text: Segments text into words and non-text segments.
    validator: Validates the romanized text.
    convert_text: Converts text between different romanization methods.
    cherry_pick: Selectively processes text based on specific criteria.
    syllable_count: Counts the number of syllables in the text.
    detect_method: Detects the romanization method used in the text.

Usage Example:
    >>> from RoManTools import convert_text
    >>> text = "Zhongguo ti'an tianqi"
    >>> converted_text = convert_text(text, from_method='py', to_method='wg')
    >>> print(converted_text)

Author:
    Jeff Heller <jsheller@princeton.edu>

Version:
    1.0.0
"""

from .utils import segment_text, validator, convert_text, cherry_pick, syllable_count, detect_method

__all__ = ['segment_text', 'validator', 'convert_text', 'cherry_pick', 'syllable_count', 'detect_method']
