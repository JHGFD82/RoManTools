# main.py

import argparse
from Tools.utils import syllable_count
from Tools.conversion import RomanizationConverter


def main():
    parser = argparse.ArgumentParser(description='Chinese Romanization Tools')

    parser.add_argument('action', choices=['count_syllables', 'convert'], help='Action to perform')
    parser.add_argument('text', type=str, help='Text to process')
    parser.add_argument('--method', type=str, choices=['PY', 'WG'], default='PY',
                        help='Romanization method (default: PY)')
    parser.add_argument('--convert', type=str, choices=['PYWG', 'WGPY'], help='Conversion method (PYWG or WGPY)')
    parser.add_argument('--skip_count', action='store_true', help='Skip counting syllables')
    parser.add_argument('--method_report', action='store_true', help='Report the romanization method in the output')
    parser.add_argument('--crumbs', action='store_true', help='Include step-by-step analysis in the output')
    parser.add_argument('--error_skip', action='store_true', help='Skip errors instead of aborting')
    parser.add_argument('--error_report', action='store_true', help='Include error messages in the output')
    parser.add_argument('--cherry_pick', type=str, choices=['PYWG', 'WGPY'],
                        help='Convert only identified, valid syllables (best for converting paragraphs with multiple '
                             'languages)')

    args = parser.parse_args()

    if args.action == 'count_syllables':
        result = syllable_count(
            text=args.text,
            skip_count=args.skip_count,
            method=args.method,
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
