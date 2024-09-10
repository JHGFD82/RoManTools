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

### `cherry_pick`

Convert only identified romanized Chinese terms in the given text, excluding any English words or those in a stopword list.

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

**Returns:**
- `str`: The detected standard(s) as either a single standard or a list of multiple standards.

**Example:**
```python
from RoManTools.utils import detect_method

result = detect_method("Bai Juyi")
print(result)  # Output: "py"
```

### `validate_text`

Validate the supplied text.

**Arguments:**
- `text` (str): The text to be validated.
- `method` (str): The romanization method of the input text.

**Returns:**
- `bool`: True if the text is valid, False otherwise.

**Example:**
```python
from RoManTools.utils import validate_text

result = validate_text("Bai Julyi", "py")
print(result)  # Output: False
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