# Input Requirements

This document outlines the requirements for successful use of the RoManTools package. Its main focus is on ensuring proper text input based on the romanization method being analyzed. These rules run parallel to the established methods of handling ambiguous tones and letter pairings.

## Important Notes

There is no restriction for the use of the various forms of apostrophe marks or dashes, however the output of the code will always result with the foot mark (') or the hyphen (-). These rules do not apply when using the detect_method feature, however they can be used as guidelines for how romanization methods are detected by RoManTools.

## Pinyin Input Requirements

Pinyin can be entered without use of supplementary punctuation. RoManTools is designed to detect initials and finals based on the transition from vowels to consonants ("Xiaoyu" -> `['Xiao', 'yu']`), and is also able to handle "n," "ng," and "er" finals ("Luanfeng" -> `['Luan', 'feng']`, "Yongtao" -> `['Yong', 'tao']`, "Sheer" -> `['She', 'er']`. However, in instances of tonal or spelling ambiguity it is highly recommended to split syllables with apostrophes ("Changan" -> `['Chan', 'gan']`, "Chang'an" -> `['Chang', 'an']`). Not doing so may lead to unexpected results.

### Examples

The code examples are written within the style of code execution within a Python console, but all rules must also be followed for command-line execution.

#### changan

```python
from RoManTools import segment_text

result = segment_text("changan", "py")
print(result)  # Output: [['chan', 'gan']]
```

```python
from RoManTools import segment_text

result = segment_text("chang'an", "py")
print(result)  # Output: [['chang', 'an']]
```

#### xian

```python
from RoManTools import segment_text, syllable_count

result = segment_text("xian", "py")
print(result)  # Output: ['xian']

result = syllable_count("xian", "py")
print(result)  # Output: [1]
```

```python
from RoManTools import segment_text, syllable_count

result = segment_text("xi'an", "py")
print(result)  # Output: [['xi', 'an']]

result = syllable_count("xian", "py")
print(result)  # Output: [2]
```

## Wade-Giles Input Requirements

RoManTools strongly recommends the use of hyphens (-) or dashes (–, —) to separate syllables in multi-syllable Wade-Giles words for optimal accuracy. While the system includes some automatic syllable boundary detection (particularly for handling 'erh' finals), explicit separation with hyphens is still the most reliable method for avoiding ambiguities with letters like "h", "ss", "ng", and vowel pairs.

All apostrophes are supported and will be counted as part of the syllable's initial; however, all variations of apostrophes entered will be converted to the foot mark (').

### Examples

The code examples are written within the style of code execution within a Python console, but all rules must also be followed for command-line execution.

#### ch'i-hsiao (recommended: with explicit hyphens)

```python
from RoManTools import segment_text

result = segment_text("ch'i-hsiao", "wg")
print(result)  # Output: [["ch'i", 'hsiao']]
```

#### Simple cases may work without hyphens

```python
from RoManTools import segment_text

# Simple cases might work, but hyphens are still recommended
result = segment_text("ch'ihsiao", "wg")
print(result)  # Output: [["ch'ih", 'siao']]
```
