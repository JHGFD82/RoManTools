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

Every tool ("action") contained within RoManTools involves Chunk Processing. A "chunk" is a block of text representing a single word that includes letters and may or may not include apostrophes or dashes depending on the romanization method specified by action parameters. RoManTools uses [Regular Expressions](https://regexr.com/) to create chunks from inputted text in two steps:

1. Splitting text into individual words ("chunks")
2. Splitting words into syllables ("segments") if supported symbols are found (e.g., apostrophes and dashes for Pinyin, dashes for Wade-Giles)

Numbers, other symbols, and spaces are separated into their own blocks and are discarded, with the exception of actions that have the `error_skip` parameter marked as `True`. A "segment" may include multiple syllables if dashes or apostrophes are not supplied.

Please see [Input_Requirements.md](Input_Requirements.md) for details on what is required for inputted text per romanization method.

### Example

Entered text:

`Huli gei ji bai nian.`

Returned chunks with `error_skip` set to `False`:

`[['hu', 'li'], ['gei'], ['ji'], ['bai'], ['nian']]`

Returned chunks with `error_skip` set to `True`:

`[['hu', 'li'], ' ', ['gei'], ' ', ['ji'], ' ', ['bai'], ' ', ['nian'], '.']`

---

### 1.2. Syllable Processing

Each segment is converted into one or more Syllable objects. A Syllable object contains parameters that store details on each syllable's structure. Conditionals that determine whether the text was inputted with capital letters or whether it was preceeded by an apostrophe or dash are detected first. This is then followed immediately with steps to analyze the text to extract a potential syllable's initial and final. Analyzation involves iterating over each letter individually.

#### Initials

The initial is detected first. An initial of a romanized Mandarin syllable can either be a consonant (`n` for `ni`) or nothing, symbolized by the `ø` symbol (`ø` for `An`). In the Syllable Processor, one or more consonants are added to the initial as they appear first, allowing for special cases such as `ss` in Wade-Giles to be detected correctly. The process stops when a vowel appears next.

#### Finals

The Syllable Processor then iterates over vowels and consonants to determine the syllable's final. A final is typically one or more vowels (`i` for `ni`, `ao` for `hao`), however a consonant may be included in the final in certain situations such as:

Pinyin & Wade-Giles:

- `n` (`chan`)
- `ng` (`chang`)

Pinyin:

- `r` when preceeded by `e` (e.g., `sheer`)

Wade-Giles:

- `rh` when preceeded by `e` (e.g., `sheerh`)
- `h` when preceeded by `i` (e.g., `Chih`)

Internal logic dictates whether a consonant appears in the final by looking ahead to see if another vowel follows the consonants. If this is true, and the preceeding vowel and consonant combination is a valid final, then the next syllable's vowel becomes the start of the next syllable. Otherwise, the current consonant being analyzed becomes the next syllable's initial.

#### Examples:

- `changan` -> `[chang, an]`
- `zhongguo` -> `[zhong, guo]`

The resulting syllable is then given a final validation check. This is performed by referencing an array of valid initial-final combinations.

Completed Syllable objects are then returned to the Chunk Generator individually, with each syllable for a word compiled into a chunk.

---

### 1.3 Conversion (Word Processing)

For actions that involve converting text between romanization standards, chunks are returned back to the action, which are then used to initialize the Word Processor. Word objects are a collection of Syllable objects and other details that determine its validity as a whole.

The first process involves creating a "preview word," which is an assembly of the syllables in lowercase letters with all apostrophes and dashes in original placement, to be used in later evaluation.

Steps are then taken to analyze the word's validity, first by checking whether all syllables are valid, and second by checking if the word is a contraction. For actions such as Cherry Pick, contractions are allowed to be converted since the only invalid text in the word appears after the apostrophe in the last Syllable object. `s`, `d`, and `ll` are considered supported contractions by RoManTools, with all other contractions marked as invalid.

#### Stopwords

One final check is performed which compares the preview word to a list of stopwords to ensure that the word is able to be converted. The stopword list was generated by a separate process, as detailed in the Jupyter Notebook for the protogenesis of the [Chinese Syllable Count Generator](https://github.com/JHGFD82/ChineseSyllableCountGeneratorDraftNotes/blob/master/Chinese%20Syllable%20Count%20Generator.ipynb), combining the NLTK library for a list of English words that could be considered valid romanized Mandarin accidentally, and the Wiktionary API which added words with Mandarin, Cantonese, Chinese, Pinyin, or Wade-Giles etymologies. These latter terms were necessary due to colloquial usage of terms that should not be converted under any circumstances (e.g., `China`, `Beijing`). Other words were manually added upon further testing and determined to be exceedingly rare by various Chinese language experts at Princeton University (e.g., `route`, `we've`, `we're`).

Conversion of syllables is then performed, skipping over contractions, and returning the converted text back to each syllable. In case of conversion errors, `(!)` is returned next to the invalid syllable, to be replaced later by more meaningful feedback on what the specific error might be in the supplied text.

Syllables are capitalized if they were inputted with capital letters. Dashes and apostrophes are also returned to the text if they were included and are not part of the romanization process (e.g., `second-class`, `Shutan's`). The following logic is then applied for multi-syllable words based on the target romanization method:

#### Pinyin:

- Apostrophes added when a vowel ends one syllable and begins the following syllable (`[ti, an]` -> `ti'an`)
- Apostrophes added when `er`, `n`, or `ng` are followed by a vowel (`['chang', 'an']` -> `chang'an`)

#### Wade-Giles:

- Dashes added for all multi-Syllable-object words, with the exception of contractions (`['Chih', 'p'ing', "'s"]` -> `Chih-p'ing's`)

The concatenated word is then sent back to the action, which combines it into either a final string with spaces separating each converted term, or with all original symbols and spacing for the Cherry Pick action.

## Actions

Each action receives chunks from the Chunk Generator and treats the resulting groups of Syllable objects in different ways, all of which are narrativized below.

### 2.1. Segment Text

Inputted text is returned from the Chunk Generator as a list comprised of lists of words. Each embedded list contains each syllable for multi-syllable words. In cases where the `error_skip` parameter is set to `True`, spaces and symbols are returned as ungrouped strings in the list.

### Example

Entered text:

`Huli gei ji bai nian.`

Default result:

`[['hu', 'li'], ['gei'], ['ji'], ['bai'], ['nian']]`

Result with `error_skip` set to `True`:

`[['hu', 'li'], ' ', ['gei'], ' ', ['ji'], ' ', ['bai'], ' ', ['nian'], '.']`

### 2.2. Validator

A simple boolean is returned if all inputted text is marked as valid. The `per_word` parameter will return a detailed list of inputted words separated and each syllable's validity included.

### Example

Entered text:

`Huli gei ji bai nion.`

Default result:

`False`

Result with `per_word` set to `True`:

`[{'word': 'huli', 'syllables': ['hu', 'li'], 'valid': [True, True]}, {'word': 'gei', 'syllables': ['gei'], 'valid': [True]}, {'word': 'ji', 'syllables': ['ji'], 'valid': [True]}, {'word': 'bai', 'syllables': ['bai'], 'valid': [True]}, {'word': 'nion', 'syllables': ['ni', 'on'], 'valid': [True, False]}]`
