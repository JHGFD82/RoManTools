from typing import List, Set, Tuple
from .config import Config
from .syllable import Syllable
from .conversion import RomanizationConverter

class WordProcessor:
    def __init__(self, config: Config, convert_from: str, convert_to: str, stopwords: Set[str]):
        self.config = config
        self.convert_from = convert_from
        self.convert_to = convert_to
        self.stopwords = stopwords
        self.converter = RomanizationConverter(f"{convert_from}_{convert_to}")

    def create_word(self, syllables: List[Syllable]) -> "Word":
        return Word(syllables, self)

class Word:
    def __init__(self, syllables: List[Syllable], processor: WordProcessor):
        self.syllables = syllables
        self.processor = processor
        self.processed_syllables = []
        self.supported_contractions = {"s", "d", "ll"}
        self.unsupported_contractions = {"m", "t"}
        self.preview_word = self._create_preview_word()
        self.final_word = ""
        self.valid = self.all_valid()
        self.contraction = self.is_contraction()

    def all_valid(self) -> bool:
        return all(syl.valid for syl in self.syllables)

    def is_contraction(self) -> bool:
        return all(syl.valid for syl in self.syllables[:-1]) and \
               (self.syllables[-1].has_apostrophe and self.syllables[-1].full_syllable in self.supported_contractions)

    def _create_preview_word(self) -> str:
        word_parts = []
        for syl in self.syllables:
            if syl.has_apostrophe:
                word_parts.append("'" + syl.full_syllable)
            elif syl.has_dash:
                word_parts.append("-" + syl.full_syllable)
            else:
                word_parts.append(syl.full_syllable)
        return "".join(word_parts)

    def convert(self):
        if (self.valid or self.contraction) and self.preview_word not in self.processor.stopwords:
            for syl in self.syllables:
                if syl.valid:
                    self.processed_syllables.append((self.processor.converter.convert(syl.full_syllable), syl))
                else:
                    self.processed_syllables.append((syl.full_syllable, syl))
        else:
            self.processed_syllables = [(syl.full_syllable, syl) for syl in self.syllables]

    def apply_caps(self):
        self.processed_syllables = [(syl[1].apply_caps(syl[0]), syl[1]) for syl in self.processed_syllables]

    def add_symbols(self):
        vowels = {'a', 'e', 'i', 'o', 'u', 'ü', 'v', 'ê', 'ŭ'}

        if (self.valid or self.contraction) and self.preview_word not in self.processor.stopwords:
            self.final_word = self.processed_syllables[0][0]
            count_of_syllables = len(self.processed_syllables) + 1 if self.contraction else len(self.processed_syllables)
            for i in range(1, count_of_syllables):
                if i >= len(self.processed_syllables):
                    break

                prev_syllable = self.processed_syllables[i - 1][0]
                curr_syllable = self.processed_syllables[i][0]

                if self.processor.convert_to == 'py' and self.processed_syllables[i][1].valid:
                    if (prev_syllable[-1] in vowels and curr_syllable[0] in vowels) or \
                            (prev_syllable.endswith('er') and curr_syllable[0] in vowels) or \
                            (prev_syllable[-1] == 'n' and curr_syllable[0] in vowels) or \
                            (prev_syllable.endswith('ng') and curr_syllable[0] in vowels):
                        self.final_word += "'" + curr_syllable
                    else:
                        self.final_word += curr_syllable
                elif self.processor.convert_to == 'wg' and not self.contraction:
                    self.final_word += "-" + curr_syllable if self.processed_syllables[i][1].valid else curr_syllable
        else:
            self.final_word = "".join([syl[0] for syl in self.processed_syllables])

    def process_syllables(self) -> str:
        self.convert()

        self.apply_caps()

        self.add_symbols()

        return self.final_word