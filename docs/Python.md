# RoManTools Utilities

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