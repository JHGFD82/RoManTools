import argparse
from Tools.utils import syllable_count
from Tools.conversion import RomanizationConverter


def main():
    parser = argparse.ArgumentParser(description='Chinese Romanization Tools')

    # REQUIRED PARAMETERS

    parser.add_argument('text', type=str, help='Text to process')
    parser.add_argument('action', choices=['count_syllables', 'convert', 'convert_between'], help='Action to perform')

    # TOOL SELECTION PARAMETERS

    parser.add_argument('--skip_count', action='store_true', help='Skip counting syllables')
    parser.add_argument('--method_report', action='store_true', help='Report the romanization method in the output')
    parser.add_argument('--cherry_pick', type=str, choices=['pinyin', 'wade-giles', 'yale'], help='Convert only identified, valid syllables (enables --error_skip)')

    # CONDITIONAL PARAMETERS

    parser.add_argument('--method', type=str, choices=['pinyin', 'wade-giles', 'yale'], help='Romanization method (default: Pinyin)')
    parser.add_argument('--from_method', type=str, choices=['pinyin', 'wade-giles', 'yale'], help='Source romanization method (required for convert_between)')
    parser.add_argument('--to_method', type=str, choices=['pinyin', 'wade-giles', 'yale'], help='Target romanization method (required for convert_between)')

    # OPTIONAL DEBUG PARAMETERS

    parser.add_argument('--crumbs', action='store_true', help='Include step-by-step analysis in the output')
    parser.add_argument('--error_skip', action='store_true', help='Skip errors instead of aborting (default: True if --cherry_pick is used)')
    parser.add_argument('--error_report', action='store_true', help='Include error messages in the output')

    args = parser.parse_args()

    if args.action == 'count_syllables':
        result = syllable_count(
            text=args.text,
            method=args.method,
            skip_count=args.skip_count,
            method_report=args.method_report,
            crumbs=args.crumbs,
            error_skip=args.error_skip,
            error_report=args.error_report,
            convert=args.convert,
            cherry_pick=args.cherry_pick
        )
        print(result)

    elif args.action == 'convert':
        if not args.convert:
            print("Error: Conversion method (--convert) is required for the convert action.")
        else:
            converter = RomanizationConverter()  # Initialize only when needed
            result = converter.convert(args.text, args.convert)
            print(result)


if __name__ == '__main__':
    main()
