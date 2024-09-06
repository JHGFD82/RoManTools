# RoManTools - Romanized Mandarin Tools
This package comprises a set of tools designed to facilitate the handling of large datasets of romanized Mandarin text. It is currently under active development by Jeff Heller, Digital Project Specialist for the Department of East Asian Studies at Princeton University.

## Features
The primary function analyzed romanized Mandarin text by comparing the syllable count to the provided Chinese text. Initially, the goal was to validate the text entry of names of figures from the Tang dynasty. Over time, additional features were incorporated, including error handling, detection of Pinyin and Wade-Giles romanization systems, and translation between these systems, both individually and within English text.

---
## Features Planned for Version 1.0

Version 1.0 of this project will include the following features:

- **Conversion between Romanization Standards**: Support for converting between Pinyin and Wade-Giles (with Yale and additional standards to be added in future versions).
- **Cherry Pick**: Converts only identified romanized Chinese terms, excluding any English words or those in a stopword list.
- **Text Segmentation**: Segments text into meaningful chunks, a feature that will be utilized by other actions and also available for direct use by the user.
- **Syllable Count**: Counts the number of syllables per word and provides a report to the user.
- **Method Detect**: Identifies the romanization standard used in the input text and returns the detected standard(s) to the user as either a single standard or a list of multiple standards.
- **Validator**: Basic validation of supplied text.
---

## Origin
This project originated as the `syllable_count` function developed for use with the Tang History Database, led by Professor Anna Shields of the Department of East Asian Studies at Princeton University. The primary objective was to validate user input of romanized Mandarin, facilitating the incorporation of names from Harvard's Chinese Biographical Database (CBDB), under the direction of Professors Peter Bol and Michael Fuller, into our database.
