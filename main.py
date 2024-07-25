import argparse
from Tools.utils import syllable_count
from Tools.conversion import RomanizationConverter


def normalize_method(method, context='romanization'):
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
        'detect_method'
    ], help='Action to perform')
    parser.add_argument('text', type=str,
                        help='Text to process')

    # CONDITIONAL PARAMETERS (BASED ON CHOSEN ACTION)
    parser.add_argument('--convert_from', type=lambda x: normalize_method(x, 'romanization'),
                        choices=['pinyin', 'wade-giles'],
                        help='Source romanization method for convert and cherry_pick actions (pinyin/PY, wade-giles/WG)')
    parser.add_argument('--convert_to', type=lambda x: normalize_method(x, 'romanization'),
                        choices=['pinyin', 'wade-giles'],
                        help='Target romanization method for convert and cherry_pick actions (pinyin/PY, wade-giles/WG)')
    parser.add_argument('--tone_from', type=lambda x: normalize_method(x, 'tone'),
                        choices=['numeric', 'unicode'],
                        help='Source tone format for tone marking (numeric, unicode)')
    parser.add_argument('--tone_to', type=lambda x: normalize_method(x, 'tone'),
                        choices=['numeric', 'unicode'],
                        help='Target tone format for tone marking (numeric, unicode)')

    # OPTIONAL DEBUG PARAMETERS
    parser.add_argument('--crumbs',
                        help='Include step-by-step analysis in the output')
    parser.add_argument('--error_skip',
                        help='Skip errors instead of aborting (defaulted to True if --cherry_pick is used)')
    parser.add_argument('--error_report',
                        help='Include error messages in the output')

    args = parser.parse_args()

    # Handle dependencies and defaults
    if args.action == 'cherry_pick':
        args.error_skip = True

    # Validate and execute actions
    if args.action == 'convert':
        if not args.convert_from or not args.convert_to:
            parser.error("--convert_from and --convert_to are required for convert action")
        method_combination = f"{args.convert_from}_{args.convert_to}"
        converter = RomanizationConverter()
        result = converter.convert(args.text, method_combination)
        print(result)

    elif args.action == 'cherry_pick':
        if not args.convert_from or not args.convert_to:
            parser.error("--convert_from and --convert_to are required for cherry_pick action")
        result = syllable_count(
            text=args.text,
            method=args.convert_from + args.convert_to
        )
        print(result)

    elif args.action == 'tone_mark':
        if not args.tone_from or not args.tone_to:
            parser.error("--tone_from and --tone_to are required for tone_mark action")
        # Assume tone_mark function implementation
        result = tone_mark(args.text, args.tone_from, args.tone_to)
        print(result)

    elif args.action == 'pronunciation':
        result = convert_to_ipa(args.text)
        print(result)

    elif args.action == 'segment':
        result = segment_text(args.text)
        print(result)

    elif args.action == 'syllable_count':
        result = syllable_count(args.text)
        print(result)

    elif args.action == 'detect_method':
        result = detect_method(args.text)
        print(result)


if __name__ == '__main__':
    main()
