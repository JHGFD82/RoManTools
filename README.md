# RoManTools - Romanized Mandarin Tools

This package comprises a set of tools designed to facilitate the handling of datasets containing romanized Mandarin text. It is currently under active development by Jeff Heller, Digital Project Specialist for the Department of East Asian Studies at Princeton University.

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

## Possible Future Goals (suggestions welcome!)

* **Feedback**: Provide meaningful and specific error messages for incorrect syntax (e.g., `missing or invalid final: chy`, `extraneous characters: "(2)"`, `Xui is not a valid Wade-Giles syllable.`).
* **IPA Pronunciation**: Convert between romanized text and the International Phonetic Alphabet.
* **Tone Marking Conversion**: Convert between tone marking systems (numerical and IPA).
* **Audio Pronunciation**: Produce audio recordings of inputted text.
* **Flashcards/Quizzes**: Gamification of text input and pronunciation.
* To submit suggestions for future updates, contact main developer Jeff Heller via [Github issues](https://github.com/JHGFD82/RoManTools/issues) or via [e-mail](mailto:jh43@princeton.edu).

## Origin

This project originated as the `syllable_count` function developed for use with the Tang History Database, led by Professor Anna Shields of the Department of East Asian Studies at Princeton University. The objective was to validate user input of romanized Mandarin, facilitating the incorporation of data from Harvard University's Chinese Biographical Database (CBDB). By analyzing the syllable structure of romanized Mandarin strings and comparing them to corresponding Chinese characters, the function initially focused on validating the entry of Tang dynasty figures' names. As the project evolved, it expanded to include robust error handling, detection of both Pinyin and Wade-Giles romanization systems, and cross-system translation, even within mixed English text. The motivation to release this tool as a publicly available package stems from the need for a fast, efficient solution to validate romanized Mandarin text, promoting consistency in future datasets and ensuring flawless adherence to romanization standards.
