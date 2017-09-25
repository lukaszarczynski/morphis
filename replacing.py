import random
from typing import List, Tuple, Dict

from os.path import isfile

import grammar_category
import morphosyntactic
import tokenization

DEBUG = False


class Replacing:
    def __init__(self,
                 copypasta: List[str],
                 replacement_words: List[Tuple[Dict, grammar_category.Gender, float]],
                 morphosyntactic_dictionary: morphosyntactic.Morphosyntactic):
        self.current_word = None  # type: morphosyntactic.AmbiguousWord
        self.previous_word = None
        self.next_word = None  # TODO: update this field
        self.pasta = copypasta
        self.replacement_words = replacement_words
        self.morph = morphosyntactic_dictionary
        self.ignored_words = []
        self.load_ignored_words()
        self.selected_meaning = None  # type: morphosyntactic.Noun
        self.selected_declension = None
        if DEBUG:
            print("".join(self.pasta))

    def load_ignored_words(self, path="ignored_words.txt"):
        ignored_path = path
        if isfile(ignored_path):
            with open(ignored_path) as file:
                for line in file:
                    self.ignored_words.append(line.strip().lower())

    def replace(self) -> List[str]:
        for token_idx, token in enumerate(self.pasta[:]):
            if token.isalnum():
                if token.lower() in self.morph.morphosyntactic_dictionary:
                    raw_word = self.morph.morphosyntactic_dictionary[token.lower()]
                    self.current_word = morphosyntactic.AmbiguousWord(token, raw_word)
                    if self.current_word.certain_noun():
                        self.select_meaning()
                        self.select_declension()
                        self.print_debug_info()
                        self.pasta[token_idx] = self.replace_single_noun()  # TODO: lower/uppercase adjusting
                    self.update_iteration_data()  # TODO: maybe it should be updated even if word is not in dictionary
        return self.pasta

    def update_iteration_data(self):
        self.previous_word = self.current_word
        self.current_word = None
        self.selected_meaning = None
        self.selected_declension = None

    def replace_single_noun(self) -> str:
        replacement_words = self.filter_replacements_by_gender()
        if self.should_not_replace(replacement_words):
            return self.current_word.word

        if len(replacement_words) > 1:
            raise NotImplementedError()

        replacement_word = replacement_words[0][0]  # type: Dict[grammar_category.Number, Dict[grammar_category.Case, str]]
        inflected_word = replacement_word[self.selected_declension.number][self.selected_declension.case]
        return inflected_word

    def filter_replacements_by_gender(self):
        return list(filter(lambda replacement: replacement[1] == self.selected_meaning.gender,
                           self.replacement_words))

    def should_not_replace(self, replacement_words) -> bool:
        word_in_ignored = self.selected_meaning.base_word in self.ignored_words
        no_word_to_replace = len(replacement_words) == 0
        probability_sum = sum(replacement_word[2] for replacement_word in self.replacement_words)
        random_not_replacing = random.random() > probability_sum
        return word_in_ignored or no_word_to_replace or random_not_replacing

    def select_meaning(self):  # TODO: use unigrams
        meanings = filter(lambda meaning: isinstance(meaning, morphosyntactic.Noun), self.current_word.meanings)
        self.selected_meaning = next(meanings)

    def select_declension(self):  # TODO: create tagged bigrams and use them
        self.selected_declension = sorted(self.selected_meaning.declensions,
                                          key=lambda declension: (declension.number.value, declension.case.value))[0]

    def print_debug_info(self):
        if DEBUG:
            print("NOUN ", self.current_word.word)
            print(self.current_word)
            print(self.selected_meaning)
            print(self.selected_declension)


if __name__ == "__main__":
    DEBUG = True
    words = [({
                 grammar_category.Number.SINGULAR: {
                     grammar_category.Case.GENITIVE: 'mamuta',
                     grammar_category.Case.VOCATIVE: 'mamucie',
                     grammar_category.Case.NOMINATIVE: 'mamut',
                     grammar_category.Case.ACCUSATIVE: 'mamuta',
                     grammar_category.Case.LOCATIVE: 'mamucie',
                     grammar_category.Case.DATIVE: 'mamutowi',
                     grammar_category.Case.INSTRUMENTAL: 'mamutem'},
                 grammar_category.Number.PLURAL: {
                     grammar_category.Case.GENITIVE: 'mamutów',
                     grammar_category.Case.VOCATIVE: 'mamuty',
                     grammar_category.Case.NOMINATIVE: 'mamuty',
                     grammar_category.Case.ACCUSATIVE: 'mamuty',
                     grammar_category.Case.LOCATIVE: 'mamutach',
                     grammar_category.Case.DATIVE: 'mamutom',
                     grammar_category.Case.INSTRUMENTAL: 'mamutami'}},
             grammar_category.Gender.MASCULINE_INANIMATE,
             1.)]
    pasta = tokenization.tokenize(
        "Mój stary to fanatyk wędkarstwa. Pół mieszkania zajebane wędkami najgorsze. Średnio raz w miesiącu ktoś "
        "wdepnie w leżący na ziemi haczyk czy kotwicę i trzeba wyciągać w szpitalu bo mają zadziory na końcu. W "
        "swoim 22 letnim życiu już z 10 razy byłem na takim zabiegu. Tydzień temu poszedłem na jakieś losowe "
        "badania to baba z recepcji jak mnie tylko zobaczyła to kazała buta ściągać xD bo myślała, że "
        "znowu hak w nodze.")
    morph = morphosyntactic.Morphosyntactic("polimorfologik-2.1.txt")
    morph.create_morphosyntactic_dictionary()
    replacer = Replacing(pasta, words, morph)
    print("".join(replacer.replace()))
