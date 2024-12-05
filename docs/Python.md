# RoManTools Function Call Documentation

This document provides an overview of the utility functions available in the `utils.py` module of the RoManTools package. These functions include text processing methods such as syllable counting and text validation.

## Public Methods

### `convert`

Convert the given text from one romanization method to another.

**Arguments:**

- `text` (str): The text to be converted.
- `convert_from` (str): The romanization method of the input text.
- `convert_to` (str): The romanization method to which the text is being converted.

**Returns:**

- `str`: The converted text.

**Example:**

```python
from RoManTools.utils import convert_text

result = convert_text("Bai Juyi", "py", "wg")
print(result)  # Output: "Pai Chüi"
```

### `cherry_pick`

Convert only identified romanized Mandarin terms in the given text, excluding any English words or established spellings (e.g. China, Beijing).

**Arguments:**

- `text` (str): The text to be analyzed.
- `convert_from` (str): The romanization method of the input text.
- `convert_to` (str): The romanization method to which the text is being converted.

**Returns:**

- `str`: The text with only the identified romanized Chinese terms converted.

**Example:**

```python
from RoManTools.utils import cherry_pick

result = cherry_pick("This is a biography of Bai Juyi.", "py", "wg")
print(result)  # Output: "This is the biography of Pai Chüi."
```

### `segment_text`

Segment the text into meaningful chunks.

**Arguments:**

- `text` (str): The text to be segmented.
- `method` (str): The romanization method of the input text.

**Returns:**

- `list`: A list of segmented chunks.

**Example:**

```python
from RoManTools.utils import segment_text

result = segment_text("Bai Juyi", "py")
print(result)  # Output: ['Bai', ['Ju', 'yi']]
```

### `detect_method`

Identify the romanization standard used in the input text.

**Arguments:**

- `text` (str): The text to be analyzed.
- `per_word` (bool, optional): If set to `True`, returns detection results for each word individually.

**Returns:**

- `str` or `list`: The detected standard(s) as either a single standard or a list of multiple standards. If `per_word` is `True`, returns a list of dictionaries with detection results for each word.

**Example:**

```python
from RoManTools.utils import detect_method

# Example text to analyze
text = "Bai Juyi"

# Detect the method for the entire text
result = detect_method(text)
print(result)  # Output: "py"

# Detect the method for each word individually
result_per_word = detect_method(text, per_word=True)
print(result_per_word)  # Output: [{'word': 'Bai', 'methods': ['py']}, {'word': 'Juyi', 'methods': ['py', 'wg']}]
```

### `validate_text`

Validate the supplied text.

**Arguments:**

- `text` (str): The text to be validated.
- `method` (str): The romanization method of the input text.
- `per_word` (bool, optional): If set to `True`, returns validation results for each word individually.

**Returns:**

- `bool` or `list`: `True` if the text is valid, `False` otherwise. If `per_word` is `True`, returns a list of dictionaries with validation results for each word.

**Example:**

```python
from RoManTools.utils import validate_text

text = "Bai Julyi"
method = "py"

result = validate_text(text, method)
print(result)  # Output: False

result = validate_text(text, method, per_word=True)
print(result)  # Output: [{'word': 'bai', 'syllables': ['bai'], 'valid': [True]}, {'word': 'julyi', 'syllables': ['ju', 'lyi'], 'valid': [True, False]}]
```

### `syllable_count`

Count the number of syllables in the given text.

**Arguments:**

- `text` (str): The text to be analyzed.

**Returns:**

- `int`: The number of syllables in the text.

**Example:**

```python
from RoManTools.utils import syllable_count

result = syllable_count("Bai Juyi")
print(result)  # Output: 3
```
