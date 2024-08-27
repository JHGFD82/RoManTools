import argparse
from Tools.utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator


def normalize_method(method: str, context: str) -> str:
    """

    This method takes in two parameters: 'method' and 'context', both of type string. It returns a string as the output.

    Parameters:
        - method (str): The romanization or tone mark method to normalize.
        - context (str): The context in which the method is used ('romanization' or 'tone').

    Returns:
        - str: The normalized method.

    This method first converts the input 'method' to lowercase. It then checks if the 'method' belongs to the
    romanization methods list ['pinyin', 'py', 'wade-giles', 'wg']. If it does, it further checks the specific method
    and returns the corresponding normalized method ('py' for 'pinyin' or 'py', 'wg' for 'wade-giles' or 'wg').

    If the 'method' does not belong to the romanization methods list, it checks if it belongs to the tone methods list
    ['numeric', 'unicode']. If it does, it simply returns the method as it is.

    If neither of the above conditions is met, it checks the 'context' parameter. If the 'context' is 'romanization', it
    raises an error with a message indicating the invalid romanization method. If the 'context' is 'tone', it raises an
    error with a message indicating the invalid tone mark format.

    Note: This method uses the 'argparse' module to raise errors. Make sure to import the 'argparse' module before using
    this method.

    """
    method = method.lower()
    romanization_methods = ['pinyin', 'py', 'wade-giles', 'wg']
    tone_methods = ['numeric', 'unicode']

    if method in romanization_methods:
        if method in ['pinyin', 'py']:
            return 'py'
        elif method in ['wade-giles', 'wg']:
            return 'wg'
    elif method in tone_methods:
        return method
    else:
        if context == 'romanization':
            raise argparse.ArgumentTypeError(f"Invalid romanization method: {method}")
        elif context == 'tone':
            raise argparse.ArgumentTypeError(f"Invalid tone mark format: {method}")


def validate_arguments(args):
    """
    Validates the provided arguments based on the selected action.
    Raises appropriate errors if required arguments are missing.

    Parameters:
    - args: The parsed arguments from argparse.

    Returns:
    - None
    """
    if args.action in ['segment', 'validator', 'syllable_count', 'detect_method']:
        if not args.text:
            raise ValueError(f'The --text argument is required for the {args.action} action.')

        # Additional checks for method-related actions
        if args.action in ['convert_text', 'cherry_pick']:
            if not args.convert_from or not args.convert_to:


#  BASIC ACTIONS #
def segment_action(args):
    return segment_text(args.text, args.method, args.crumbs, args.error_skip, args.error_report)


def validator_action(args):
    return validator(args.text, args.method, args.per_word, args.crumbs, args.error_skip, args.error_report)


# CONVERSION ACTIONS #
def convert_action(args):
    method_combination = f"{args.convert_from}_{args.convert_to}"
    return convert_text(args.text, method_combination, args.crumbs, args.error_skip, args.error_report)


def cherry_pick_action(args):
    method_combination = f"{args.convert_from}_{args.convert_to}"
    return cherry_pick(args.text, method_combination, args.crumbs, True, args.error_report)


# OTHER UTILITY ACTIONS #
def syllable_count_action(args):
    return syllable_count(args.text, args.method, args.crumbs, args.error_skip, args.error_report)


def detect_method_action(args):
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
                             'detect_method process)')

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
