import argparse
from src.utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator


def normalize_method(method: str, context: str) -> str:
    """
    Normalizes and validates the romanization or tone marking method based on the provided context.

    Args:
        method (str): The romanization or tone marking method provided by the user.
        context (str): The context for the method ('romanization').

    Returns:
        str: The normalized method ('py', 'wg').

    Raises:
        argparse.ArgumentTypeError: If the method is invalid for the given context.
    """
    method = method.lower()
    romanization_methods = ['pinyin', 'py', 'wade-giles', 'wg']

    if method in romanization_methods:
        if method in ['pinyin', 'py']:
            return 'py'
        elif method in ['wade-giles', 'wg']:
            return 'wg'
    else:
        if context == 'romanization':
            raise argparse.ArgumentTypeError(f"Invalid romanization method: {method}")


def validate_arguments(args):
    """
    Validates the command-line arguments based on the selected action.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Raises:
        ValueError: If required arguments are missing for specific actions.
    """
    if args.action in ['segment', 'validator', 'syllable_count', 'detect_method']:
        if not args.text:
            raise argparse.ArgumentTypeError(f'The --text argument is required for the {args.action} action.')

        # Additional checks for method-related actions
        if args.action in ['convert_text', 'cherry_pick']:
            if not args.convert_from or not args.convert_to:
                raise argparse.ArgumentTypeError(f'Both --convert_from and --convert_to arguments are required for the '
                                                 f'{args.action} action.')


#  BASIC ACTIONS #
def segment_action(args):
    """
    Segments the text into a list of words and syllables based on the provided method.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        list: The segmented words and syllables.
    """
    return segment_text(args.text, args.method)


def validator_action(args):
    """
    Validates the romanization of the text based on the provided method.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        bool or list[dict]: The validation result, either as a boolean or detailed information per word.
    """
    return validator(args.text, args.method, args.per_word)


# CONVERSION ACTIONS #
def convert_action(args):
    """
    Converts the text between romanization methods based on the provided source and target methods.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        str: The converted text.
    """
    method_combination = f"{args.convert_from}_{args.convert_to}"
    return convert_text(args.text, method_combination)


def cherry_pick_action(args):
    """
    Converts only the terms identified as valid romanized Mandarin while leaving the rest of the text untouched.

    This function is designed to handle mixed content where English and romanized Mandarin are intermixed. It applies
    the conversion process selectively to recognized romanized Mandarin terms and skips over any other content,
    preserving it in its original form.

    Args:
        args (argparse.Namespace): Parsed command-line arguments, including text, conversion methods, and debugging
        options.

    Returns:
        str: The text with only valid romanized Mandarin terms converted according to the specified methods,
        with non-romanized content left unchanged.
    """
    method_combination = f"{args.convert_from}_{args.convert_to}"
    return cherry_pick(args.text, method_combination)


# OTHER UTILITY ACTIONS #
def syllable_count_action(args):
    """
    Counts the number of syllables in the provided romanized Mandarin text.
    Args:
        args (argparse.Namespace): Parsed command-line arguments, including text and method options.

    Returns:
        List[int]: A list containing the syllable count for each valid romanized Mandarin segment, or 0 for segments
        identified as invalid.
    """
    return syllable_count(args.text, args.method)


def detect_method_action(args):
    """
    Detects the romanization method used in the provided text. It can operate on entire text blocks or on a per-word
    basis, depending on the provided arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments, including text, method options, and per-word analysis
        flag.

    Returns:
        Union[List[str], List[Dict[str, List[str]]]]: The detected romanization methods either for the whole text or
        for each word individually if per-word analysis is enabled.
    """
    return detect_method(args.text, args.per_word)


# Map actions to functions
ACTIONS = {
    "segment": segment_action,
    "validator": validator_action,
    "convert": convert_action,
    "cherry_pick": cherry_pick_action,
    "syllable_count": syllable_count_action,
    "detect_method": detect_method_action
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
        'tone_mark',
        'pronunciation',
        'segment',
        'syllable_count',
        'detect_method',
        'validator'
    ], help='Action to perform')
    parser.add_argument('-i', '--input', type=str, dest='text', required=True,
                        help='Text to process')

    # CONDITIONAL PARAMETERS (BASED ON CHOSEN ACTION)
    parser.add_argument('--method', type=lambda x: normalize_method(x, 'romanization'),
                        help='Romanization method for functions (pinyin/py, wade-giles/wg)')
    parser.add_argument('--convert_from', type=lambda x: normalize_method(x, 'romanization'),
                        help='Source romanization method for convert and cherry_pick actions '
                             '(pinyin/py, wade-giles/wg)')
    parser.add_argument('--convert_to', type=lambda x: normalize_method(x, 'romanization'),
                        help='Target romanization method for convert and cherry_pick actions '
                             '(pinyin/py, wade-giles/wg)')
    parser.add_argument('--per_word', action='store_true',
                        help='Perform action on each word within a multi-word string (currently only supported for '
                             'detect_method and validator process)')

    # OPTIONAL DEBUG PARAMETERS
    parser.add_argument('--crumbs', action='store_true',
                        help='Include step-by-step analysis in the output')
    parser.add_argument('--error_skip', action='store_true',
                        help='Skip errors instead of aborting (defaulted to True if --cherry_pick is used)')
    parser.add_argument('--error_report', action='store_true',
                        help='Include error messages in the output')

    args = parser.parse_args()

    # Validate common arguments here
    validate_arguments(args)

    # Call the appropriate function
    print(ACTIONS[args.action](args))


if __name__ == '__main__':
    main()
