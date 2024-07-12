import argparse
from data_loader import load_csv_data, prepare_reference_data, load_stopwords
from syllable_processor import find_initial, find_final, split_syllable
from text_processor import convert_romanization, syllable_count
from utils import clean_text, log_error, display_options
import config


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Romanization Processing Tool")
    parser.add_argument('--mode', help='Mode of operation (e.g., interactive, batch)', default='interactive')
    # Add other arguments as needed
    args = parser.parse_args()

    # Load data
    pinyin_data = load_csv_data(config.PINYIN_DATA_FILE)
    pinyin_init_list, pinyin_fin_list, _ = prepare_reference_data(pinyin_data)

    wadegiles_data = load_csv_data(config.WADEGILES_DATA_FILE)
    wg_init_list, wg_fin_list, _ = prepare_reference_data(wadegiles_data)

    stopwords = load_stopwords(config.STOPWORDS_FILE)

    # Process based on the selected mode
    if args.mode == 'interactive':
        run_interactive_mode()
    elif args.mode == 'batch':
        run_batch_mode()
    # Add other modes as necessary


def run_interactive_mode():
    print("Interactive Mode")
    while True:
        user_input = input("Enter a syllable to process (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        # Process the user input here (e.g., identify initials and finals, convert syllables)
        # For example:
        initial, final = split_syllable(user_input, init_list, fin_list)
        print(f"Initial: {initial}, Final: {final}")

        # Depending on your application's functionality, add additional processing and output here


def run_batch_mode(input_file: str, output_file: str):
    print("Batch Mode")
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Process each line (which could contain one or more syllables)
            # For example, split syllables, convert them, etc.
            processed_line = process_line(line)  # process_line is a hypothetical function
            outfile.write(processed_line + '\n')

    print(f"Processing complete. Output saved to {output_file}")


if __name__ == "__main__":
    main()
