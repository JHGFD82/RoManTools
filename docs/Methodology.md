# Text Processing Methodology

This documentation details the process by which text is analyzed. Documentation provided here is a more narrativized version of docstrings and comments already supplied within the RomanTools Python code.

1. Chunk Processing
   1. Segment Generation
   2. Syllable Processing
   3. Conversion (Word Processing)
2. Actions
   1. Segment Text
   2. Validator
   3. Detect Method
   4. Syllable Count
   5. Convert
   6. Cherry Pick

## 1. Chunk Processing

### 1.1. Segment Generation

Chunk processing is a foundational step in all RoManTools actions. A **chunk** represents a single word or block of text that may include letters, apostrophes, and dashes, depending on the romanization method specified by the action parameters.

#### Key Steps

1. **Text Splitting**:
   * The input text is split into individual chunks using **Regular Expressions**.
   * Words are further divided into **segments** based on supported symbols:
     * Apostrophes and dashes (Pinyin).
     * Dashes (Wade-Giles).
2. **Symbol and Space Handling**:
   * Numbers, symbols, and spaces are separated into their own chunks.
   * These are discarded unless the `error_skip` parameter is set to `True`, in which case they are retained.
3. **Segment Definition**:
   * A **segment** can consist of one or more syllables. For example, if no apostrophes or dashes are present, multiple syllables may be grouped into a single segment.

#### Input Requirements

Details on input text requirements for each romanization method are provided in the [Input Requirements](Input_Requirements.md) documentation.

#### Examples

**Entered Text**:
`Huli gei ji bai nian.`

**Results with `error_skip=False`**:

```python
[['hu', 'li'], ['gei'], ['ji'], ['bai'], ['nian']]
```

**Results with `error_skip=True`**:

```python
[['hu', 'li'], ' ', ['gei'], ' ', ['ji'], ' ', ['bai'], ' ', ['nian'], '.']
```

By processing text into structured chunks, RoManTools enables precise analysis and manipulation for various romanization methods and text transformations.

---

### 1.2. Syllable Processing

The syllable processing step converts each segment into one or more **Syllable** objects, representing detailed structural information for each syllable. The processing includes:

1. **Initial Detection**:
   The initial part of the syllable, often a consonant (`n` in `ni`), is identified first. If no initial exists, it is represented as `ø` (e.g., `ø` for `An`). The processor appends consonants to the initial until a vowel is detected, ensuring special cases like `ss` in Wade-Giles are handled correctly.
2. **Final Detection**:
   The processor analyzes the remaining characters to identify the syllable's final. This typically consists of one or more vowels (`i` in `ni` or `ao` in `hao`), but may include consonants under specific rules. For example:

   * **Pinyin & Wade-Giles**: Final consonants like `n` (`chan`) or `ng` (`chang`).
   * **Pinyin**: `r` following `e` (e.g., `sheer`).
   * **Wade-Giles**: `rh` following `e` (`sheerh`) or `h` following `i` (`Chih`).

   The logic ensures that valid consonant-vowel pairs are included in the final, while any remaining vowels start the next syllable.
3. **Validation**:
   After constructing a Syllable object, its initial-final combination is validated against a predefined list of acceptable patterns. Invalid syllables are flagged for correction or feedback.

**Example:**

```python
# Input
segment = "zhongguo"
# Output
syllables = ["zhong", "guo"]
```

Each validated Syllable object is returned to the Chunk Processor, grouped within a chunk for further processing.

---

### 1.3. Conversion (Word Processing)

Text conversion actions use the chunks from the **Chunk Generator** to initialize the **Word Processor**, which aggregates **Syllable** objects and evaluates the validity of entire words. The conversion process involves the following steps:

1. **Preview Word Creation**:
   A "preview word" is assembled by combining syllables into lowercase text with original apostrophes and dashes retained. This serves as a basis for validation and further processing.
2. **Validation**:

   * Each syllable in the word is checked for validity.
   * Contractions, where only the final syllable is invalid (e.g., `'s`, `'d`, `'ll`), are permitted under specific actions like `Cherry Pick`.
3. **Stopword Check**:
   The word is compared against a stopword list to ensure that it does not represent a term that should not be converted (e.g., `China`, `Beijing`). This list combines English stopwords, Mandarin romanization exceptions, and manually reviewed entries.
4. **Syllable Conversion**:
   Each syllable is converted according to the target romanization method. Errors in conversion are flagged with `(!)` to indicate invalid input.
5. **Final Assembly**:

   * Capitalization is restored if present in the original input.
   * Apostrophes and dashes are inserted based on the target romanization method's rules:
     * **Pinyin**: Apostrophes separate consecutive vowels (`ti'an`).
     * **Wade-Giles**: Dashes connect all syllables (`Chih-p'ing`).

   The processed word is then combined into a final string, either preserving original spacing and symbols (`error_skip=True`) or standardizing formatting.

#### Examples

**Pinyin to Wade-Giles**:

```python
# Input
text = "Yanjing li rong bu xia sharen."
# Output
"Yen-ching li jung pu hsia sha-jen"
```

**Wade-Giles to Pinyin:**

```python
# Input
text = "Chih-p'ing's specialty is in Chinese language."
# Output
"Zhiping's specialty is in Chinese language."
```

## 2. Actions

The **Actions** in RoManTools utilize the chunks generated during **Chunk Processing** to perform various text analyses and transformations. Each action processes groups of **Syllable** objects differently, depending on its specific functionality. Below are descriptions and examples for each available action.

### 2.1. Segment Text

Splits the input text into a structured list of words and their syllables. Each embedded list represents a word, containing its syllables. If `error_skip=True`, spaces and symbols are also included as separate items.

#### Examples

**Input**:
`Huli gei ji bai nian.`

**Default Output**:

```python
[['hu', 'li'], ['gei'], ['ji'], ['bai'], ['nian']]
```

**Output with `error_skip=True`**:

```python
[['hu', 'li'], ' ', ['gei'], ' ', ['ji'], ' ', ['bai'], ' ', ['nian'], '.']
```

---

### 2.2. Validator

Checks the validity of the input text according to romanization rules. By default, it returns `True` or `False` for the entire text. With `per_word=True`, a detailed breakdown of each word and syllable’s validity is provided.

#### Examples

**Input**:
`Huli gei ji bai nion.`

**Default Output**:

```python
False
```

**Output with `per_word=True`**:

```python
[
    {'word': 'huli', 'syllables': ['hu', 'li'], 'valid': [True, True]},
    {'word': 'gei', 'syllables': ['gei'], 'valid': [True]},
    {'word': 'ji', 'syllables': ['ji'], 'valid': [True]},
    {'word': 'bai', 'syllables': ['bai'], 'valid': [True]},
    {'word': 'nion', 'syllables': ['ni', 'on'], 'valid': [True, False]}
]
```

---

### 2.3. Detect Method

Identifies which romanization methods (e.g., Pinyin, Wade-Giles) are valid for the input text. By default, it returns a list of valid methods for the entire input. With `per_word=True`, it provides detailed results for each word.

#### Examples

**Input**:
`Yanjing li rong bu xia sharen`

**Default Output**:

```python
['py']
```

**Output with `per_word=True`**:

```python
[
    {'word': 'Yanjing', 'methods': ['py']},
    {'word': 'li', 'methods': ['py', 'wg']},
    {'word': 'rong', 'methods': ['py']},
    {'word': 'bu', 'methods': ['py']},
    {'word': 'xia', 'methods': ['py']},
    {'word': 'sharen', 'methods': ['py']}
]
```

---

### 2.4. Syllable Count

Counts the number of syllables in each valid word. If a word contains any invalid syllables, it returns `[0]` for that word.

#### Example

**Input**:
`Yanjing li rong bu xia sharen`

**Output**:

```python
[2, 1, 1, 1, 1, 2]
```

---

### 2.5. Convert

Converts the input text between romanization standards. The resulting text is returned as a string, with spaces separating converted words. If `error_skip=True`, the original spaces and symbols are preserved.

#### Examples

**Pinyin to Wade-Giles**:
**Input**:
`Yanjing li rong bu xia sharen.`

**Default Output**:

```python
"Yen-ching li jung pu hsia sha-jen"
```

**Output with `error_skip=True`**:

```python
"Yen-ching   li   rong   bu   hsia   sha-jen ."
```

---

### 2.6. Cherry Pick

Selectively converts valid romanized Mandarin words while leaving invalid words unchanged. Symbols and spacing are always preserved, as this action runs with `error_skip=True` by default.

#### Example

**Wade-Giles to Pinyin**:
**Input**:
`This is the biography of Chih-p'ing Chou. Chih-p'ing's specialty was in Chinese language.`

**Output:**

```python
"This is the biography of Zhiping Zhou. Zhiping's specialty was in Chinese language."
```
