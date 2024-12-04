"""
This module serves as the main entry point for the RoManTools package, providing command-line
interface (CLI) functionality for various romanized Mandarin text processing actions.

Functions:
    main(): The main entry point for the script. Sets up command-line argument parsing and calls
            the appropriate function based on the provided arguments.

Usage Example:
    $ romantools segment -i "Zhongguo ti'an tianqi" -m py
    [['zhong', 'guo'], ['ti', 'an'], ['tian', 'qi']]

Author:
    Jeff Heller <jsheller@princeton.edu>

Version:
    1.0.0
"""

import argparse
from .utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator


def _normalize_method(method: str, context: str) -> str:
    """
    Normalizes the romanization method string to a standard format.

    Args:
        method (str): The romanization method string.
        context (str): The context in which the method is being used.

    Returns:
        str: The normalized romanization method string.

    """
    method = method.lower()
    method_map = {
        'pinyin': 'py',
        'py': 'py',
        'wade-giles': 'wg',
        'wg': 'wg'
    }
    if method in method_map:
        return method_map[method]
    else:
        if context == 'romanization':
            raise argparse.ArgumentTypeError(f"Invalid romanization method: {method}")


def _validate_arguments(args):
    """
    Validates the arguments based on the chosen action.

    Args:
        args: The parsed command-line arguments.

    Returns:
        None
    """
    if args.action in ['segment', 'validator', 'syllable_count', 'detect_method']:
        if not args.text:
            raise argparse.ArgumentTypeError(f'The --text argument is required for the {args.action} action.')

        # Additional checks for method-related actions
        if args.action in ['convert_text', 'cherry_pick']:
            if not args.convert_from or not args.convert_to:
                raise argparse.ArgumentTypeError(f'Both --convert_from and --convert_to arguments are required for the '
                                                 f'{args.action} action.')


# ACTION FUNCTIONS #
def _segment_action(args):
    return segment_text(args.text, args.method, args.crumbs, args.error_skip, args.error_report)


def _validator_action(args):
    return validator(args.text, args.method, args.per_word, args.crumbs, args.error_skip, args.error_report)


def _convert_action(args):
    return convert_text(args.text, args.convert_from, args.convert_to, args.crumbs, args.error_skip, args.error_report)


def _cherry_pick_action(args):
    return cherry_pick(args.text, args.convert_from, args.convert_to, args.crumbs, True, args.error_report)


def _syllable_count_action(args):
    return syllable_count(args.text, args.method, args.crumbs, args.error_skip, args.error_report)


def _detect_method_action(args):
    return detect_method(args.text, args.per_word, args.crumbs, args.error_skip, args.error_report)


# Map actions to functions
ACTIONS = {
    "segment": _segment_action,
    "validator": _validator_action,
    "convert": _convert_action,
    "cherry_pick": _cherry_pick_action,
    "syllable_count": _syllable_count_action,
    "detect_method": _detect_method_action
}


def main():
    """
    The main entry point for the script. Sets up command-line argument parsing and calls the appropriate function.

    Raises:
        argparse.ArgumentError: If invalid arguments are provided.
    """
    parser = argparse.ArgumentParser(description='RoManTools: Romanized Mandarin Tools')

    # REQUIRED PARAMETERS
    parser.add_argument('action', choices=[
        'convert',
        'cherry_pick',
        'segment',
        'syllable_count',
        'detect_method',
        'validator'
    ], help='Action to perform')
    parser.add_argument('-i', '--input', type=str, dest='text', required=True,
                        help='Text to process')

    # CONDITIONAL PARAMETERS (BASED ON CHOSEN ACTION)
    parser.add_argument('-m', '--method', type=lambda x: _normalize_method(x, 'romanization'),
                        help='Romanization method for functions (pinyin/py, wade-giles/wg)')
    parser.add_argument('-f', '--convert_from', type=lambda x: _normalize_method(x, 'romanization'),
                        help='Source romanization method for convert and cherry_pick actions '
                             '(pinyin/py, wade-giles/wg)')
    parser.add_argument('-t', '--convert_to', type=lambda x: _normalize_method(x, 'romanization'),
                        help='Target romanization method for convert and cherry_pick actions '
                             '(pinyin/py, wade-giles/wg)')

    # OPTIONAL PARAMETERS
    parser.add_argument('-w', '--per_word', action='store_true',
                        help='Perform action on each word within a multi-word string (currently only supported for '
                             'detect_method and validator process)')

    # OPTIONAL DEBUG PARAMETERS
    parser.add_argument('-C', '--crumbs', action='store_true',
                        help='Include step-by-step analysis in the output')
    parser.add_argument('-S', '--error_skip', action='store_true',
                        help='Skip errors instead of aborting (defaulted to True if --cherry_pick is used)')
    parser.add_argument('-R', '--error_report', action='store_true',
                        help='Include error messages in the output')

    args = parser.parse_args()

    # Validate common arguments here
    _validate_arguments(args)

    # Call the appropriate function
    print(ACTIONS[args.action](args))


if __name__ == '__main__':
    main()
