"""
This module serves as the main entry point for the RoManTools package, providing command-line
interface (CLI) functionality for various romanized Mandarin text processing actions.

Functions:
    main(): The main entry point for the script. Sets up command-line argument parsing and calls
            the appropriate function based on the provided arguments.

Usage Example:
    $ romantools segment -i "Zhongguo ti'an tianqi" -m py
    [['zhong', 'guo'], ['ti', 'an'], ['tian', 'qi']]
"""

import argparse
import sys
from typing import Optional, List, Dict, Callable
from .config import Config
from .utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator
from .constants import method_shorthand_to_full, supported_methods, supported_actions, supported_config


def _normalize_method(method: str) -> str:
    """
    Normalizes the romanization method string to a standard format.

    Args:
        method (str): The romanization method string.

    Returns:
        str: The normalized romanization method string.
    """

    method = method.lower()
    if method in supported_methods:
        return supported_methods[method]['shorthand']
    if method in method_shorthand_to_full:
        return method
    raise argparse.ArgumentTypeError(f"Invalid romanization method: {method}")


def _validate_arguments(args: argparse.Namespace):
    """
    Validates the arguments based on the chosen action.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        None
    """

    # Additional checks for method-related actions
    if args.action in ['segment', 'validator', 'syllable_count']:
        if not args.method:
            print(f'The --method argument is required for the {args.action} action.', file=sys.stderr)
            raise SystemExit(2)

    if args.action in ['convert', 'cherry_pick']:
        if not args.convert_from or not args.convert_to:
            print(f'Both --convert_from and --convert_to arguments are required for the {args.action} action.', file=sys.stderr)
            raise SystemExit(2)


# ACTION FUNCTIONS #
def _segment_action(args: argparse.Namespace, config: Config):
    return segment_text(args.text, args.method, config)


def _validator_action(args: argparse.Namespace, config: Config):
    return validator(args.text, args.method, args.per_word, config)


def _convert_action(args: argparse.Namespace, config: Config):
    return convert_text(args.text, args.convert_from, args.convert_to, config)


def _cherry_pick_action(args: argparse.Namespace, config: Config):
    config.error_skip = True  # Set the specific value for cherry_pick
    return cherry_pick(args.text, args.convert_from, args.convert_to, config)


def _syllable_count_action(args: argparse.Namespace, config: Config):
    return syllable_count(args.text, args.method, config)


def _detect_method_action(args: argparse.Namespace, config: Config):
    return detect_method(args.text, args.per_word, config)


# Map actions to functions
ACTIONS: Dict[str, Callable[[argparse.Namespace, Config], object]] = {
    "segment": _segment_action,
    "validator": _validator_action,
    "convert": _convert_action,
    "cherry_pick": _cherry_pick_action,
    "syllable_count": _syllable_count_action,
    "detect_method": _detect_method_action
}


def main(arg_list: Optional[List[str]] = None):
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
    parser.add_argument('-m', '--method', type=_normalize_method,
                        help='Romanization method for functions (pinyin/py, wade-giles/wg)')
    parser.add_argument('-f', '--convert_from', type=_normalize_method,
                        help='Source romanization method for convert and cherry_pick actions '
                             '(pinyin/py, wade-giles/wg)')
    parser.add_argument('-t', '--convert_to', type=_normalize_method,
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

    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    # Validate common arguments here
    _validate_arguments(args)

    # Create the Config object
    config = Config(crumbs=args.crumbs, error_skip=args.error_skip, error_report=args.error_report)

    # Print starting timestamp if crumbs is enabled
    from datetime import datetime
    config.print_crumb(level=1, stage='Start', message=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Use alias_maps to get pretty action name
    pretty_action = supported_actions[args.action]['pretty']
    config.print_crumb(level=1, stage='Performing action', message=f'{pretty_action}')

    # Report configuration if crumbs is enabled
    enabled_configs = [supported_config[key]['pretty'] for key, val in config.__dict__.items() if val and key in supported_config]
    if enabled_configs:
        config.print_crumb(level=1, stage='Configuration', message=', '.join(enabled_configs))
        config.print_crumb(footer=True)

    # Call the appropriate function with the Config object
    result = ACTIONS[args.action](args, config)

    # Print ending timestamp if crumbs is enabled
    config.print_crumb(level=1, stage='End', message=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    print(str(result))


if __name__ == '__main__':  # pragma: no cover
    main()
