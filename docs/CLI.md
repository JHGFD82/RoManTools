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
RoManTools can be executed from the command line by first navigating to the location where you have downloaded RoManTools and running the following command inside the `src` folder:

`python main.py`

Or on systems with installations of both Python 2 and 3:

`python3 main.py`

You will receive an error since required arguments are not being supplied, however this will verify that you executed the command in the correct location. 

## 2. Commands
`convert`: Support for converting between Pinyin and Wade-Giles (with Yale and additional standards to be added in future versions).

`cherry_pick`: Converts only identified romanized Chinese terms, excluding any English words or those in a stopword list.

`segment`: Segments text into meaningful chunks, a feature that will be utilized by other actions and also available for direct use by the user.

`syllable_count`: Counts the number of syllables per word and provides a report to the user.

`detect_method`: Identifies the romanization standard used in the input text and returns the detected standard(s) to the user as either a single standard or a list of multiple standards.

`validator`: Basic validation of supplied text.

## 3. Required Arguments
### Note: "methods" refers to currently supported romanization methods:
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
- `python main.py convert --input "Bai Juyi" --convert_from py --convert_to wg`
  - Output: `Pai Chüi`

### Cherry Pick
- `python main.py cherry_pick -i "This is a biography of Bai Juyi." -f py -t wg`
  - Output: `This is the biography of Pai Chüi.`

### Segment
- `python main.py segment -i "Bai Juyi" -m py`
  - Output: `['Bai', ['Ju', 'yi']]`

### Syllable Count
- `python main.py syllable_count -i "Bai Juyi" -m py`
  - Output: `[1, 2]`

### Detect Method
- `python main.py detect_method -i "Bai Juyi"`
  - Output: `py`
- `python main.py detect_method -i "Bai Juyi" --per_word`
  - Output: `[{'word': 'Bai', 'methods': ['py']}, {'word': 'Juyi', 'methods': ['py', 'wg']}]`

### Validator
- `python main.py validator -i "Bai Julyi" -m py`
  - Output: `False`
- `python main.py validator -i "Bai Julyi" -m py --per_word`
  - Output: `[{'word': 'bai', 'syllables': ['bai'], 'valid': [True]}, {'word': 'julyi', 'syllables': ['ju', 'lyi'], 'valid': [True, False]}]`

### Debugging Example
- `python main.py validator -i "Bai Julyi" -m py -wC`
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
  - **Solution**: Ensure you are providing a valid command after `python main.py`.
- **Error**: `Invalid method`
  - **Solution**: Check that the method provided is one of the supported methods (`py`, `pinyin`, `wg`, `wade-giles`).

For further assistance, refer to the official documentation or contact main developer Jeff Heller via [Github issues](https://github.com/JHGFD82/RoManTools/issues) or via [e-mail](mailto:jh43@princeton.edu).