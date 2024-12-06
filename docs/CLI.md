# Command-line Execution

## Table of Contents

1. [Initial Execution Instruction](#1-initial-execution-instruction)
2. [Commands](#2-commands)
3. [Required Arguments](#3-required-arguments)
4. [Optional Parameters for Additional Features](#4-optional-parameters-for-additional-features)
5. [Optional Parameters for Debugging Purposes](#5-optional-parameters-for-debugging-purposes)
6. [Examples](#examples)
7. [Common Errors and Troubleshooting](#common-errors-and-troubleshooting)

## 1. Initial Execution Instruction

After installing the package through pip or conda, RoManTools can be executed from the command line by typing `RoManTools` in your terminal or Jupyter Notebooks. Please note that use of capital letters in package names is unconventional—the vast majority of Python packages are written in lowercase.

Upon running `RoManTools` you will receive an error. This is because required arguments are not being supplied. However, all supported arguments will be listed.

## 2. Commands

`convert`: Support for converting between Pinyin and Wade-Giles (with Yale and additional standards to be added in future versions).

`cherry_pick`: Converts only identified romanized Chinese terms, excluding any English words or those in a stopword list.

`segment`: Segments text into meaningful chunks, a feature that will be utilized by other actions and also available for direct use by the user.

`syllable_count`: Counts the number of syllables per word and provides a report to the user.

`detect_method`: Identifies the romanization standard used in the input text and returns the detected standard(s) to the user as either a single standard or a list of multiple standards.

`validator`: Basic validation of supplied text.

## 3. Required Arguments

### Note: "methods" refers to currently supported Mandarin romanization methods:

- Pinyin (entered as `py` or `pinyin`)
- Wade-Giles (entered as `wg` or `wage-giles`)

`-i / --input`: The text to be analyzed/converted.

`-m / --method`: The romanization method of the supplied text.

`-f / --convert_from`: The originating romanization method to be analyzed.

`-t / --convert_to`: The method to which the text is being converted.

## 4. Optional Parameters for Additional Features

`-w / --per_word`: For supported actions, return results of analysis on a per-word basis. Performing an action without this parameter will result in a single response.

## 5. Optional Parameters for Debugging Purposes*

### *Note: Currently, no parameters currently function. This section is for the purpose of detailing features from a future release.

`-C / --crumbs`: Reports a breadcrumb trail from the analysis process.


## Examples

### Convert

- `RoManTools convert --input "Bai Juyi" --convert_from py --convert_to wg`
  - Output: `Pai Chüi`

### Cherry Pick

- `RoManTools cherry_pick -i "This is a biography of Bai Juyi." -f py -t wg`
  - Output: `This is the biography of Pai Chüi.`

### Segment

- `RoManTools segment -i "Bai Juyi" -m py`
  - Output: `['Bai', ['Ju', 'yi']]`

### Syllable Count

- `RoManTools syllable_count -i "Bai Juyi" -m py`
  - Output: `[1, 2]`

### Detect Method

- `RoManTools detect_method -i "Bai Juyi"`
  - Output: `py`
- `RoManTools detect_method -i "Bai Juyi" --per_word`
  - Output: `[{'word': 'Bai', 'methods': ['py']}, {'word': 'Juyi', 'methods': ['py', 'wg']}]`

### Validator

- `RoManTools validator -i "Bai Julyi" -m py`
  - Output: `False`
- `RoManTools validator -i "Bai Julyi" -m py --per_word`
  - Output: `[{'word': 'bai', 'syllables': ['bai'], 'valid': [True]}, {'word': 'julyi', 'syllables': ['ju', 'lyi'], 'valid': [True, False]}]`

### Debugging Example (see above note in Section 5)

- `RoManTools validator -i "Bai Julyi" -m py -wC`
  - Output:
    ```
    ### Analyzing Bai Julyi ###
    # Processing Bai
    # Initial: B
    # Final: ai
    # Valid: True
    ```

## Common Errors and Troubleshooting

- **Error**: `No command supplied`
  - **Solution**: Ensure you are providing a valid command after `RoManTools`.
- **Error**: `Invalid method`
  - **Solution**: Check that the romanization method provided is one of the supported methods (`py`, `pinyin`, `wg`, `wade-giles`).

For further assistance, refer to the official documentation or contact main developer Jeff Heller via [Github issues](https://github.com/JHGFD82/RoManTools/issues) or via [e-mail](mailto:jh43@princeton.edu).
