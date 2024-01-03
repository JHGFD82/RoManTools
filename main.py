import argparse
from data_loader import load_csv_data, prepare_reference_data, load_stopwords
from syllable_processor import find_initial, find_final
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
    # Implement the interactive mode logic
    # This could involve prompting the user for input, displaying results, etc.


def run_batch_mode():
    print("Batch Mode")
    # Implement the batch processing logic
    # This could involve reading from files, processing in bulk, etc.


if __name__ == "__main__":
    main()
