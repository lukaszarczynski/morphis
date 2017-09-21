from collections import defaultdict
import sys
from typing import (
    List,
    Set,
    Tuple
)

CONSOLE_WIDTH = 80
DICT_LEN = 4811854


def progress_bar(console_width=CONSOLE_WIDTH):
    """Draw console progress bar"""
    already_printed = 0
    print(" " * (console_width - 1), "|", sep="")
    print(" " * (console_width - 1), "|", "\b" * console_width, sep="", end="")

    def print_progress(progress):
        """Draw one character into progress bar if needed"""
        nonlocal already_printed
        if progress >= already_printed / console_width:
            print("=", end='')
            sys.stdout.flush()
            already_printed += 1
    return print_progress




class Meaning():
    """Represents one of possible meanings of given word,
    where meaning is map from given word to base word,
    and there is exactly one part of speech associated with this meaning"""

    def __init__(self, word: str, base_word: str, tags: List[str]):
        self.word = word
        self.base_word = base_word
        self.unfiltered_tags = Meaning.fix_tags(tags)
        self.part_of_speech = self.unfiltered_tags[0][0]

    def __str__(self):
        return "(meaning: {0}, base_word: {1}, unfiltered_tags: {2})".format(self.word, self.base_word, self.unfiltered_tags)

    @staticmethod
    def fix_tags(tags: List[str]) -> List[List[str]]:
        """Splits each tagset with non-atomic elements into multiple tagsets"""
        new_tags = []
        for tag in tags:
            tag = tag.split(":")
            if tag[0] in AmbiguousWord.noun_types and "." in tag[2]:
                cases = tag[2].split(".")
                for case in cases:
                    new_tags.append(tag[:2] + [case] + tag[3:])
            else:
                new_tags.append(tag)
        return new_tags


class Noun(Meaning):
    ...


class AmbiguousWord:
    """Stores multiple possible meanings of given word"""
    def __init__(self, original_word: str, meanings: List):
        self.word = original_word
        self.meanings = []  # type: List[Meaning]
        fixed_meanings = []
        for raw_meaning in meanings:
            fixed_meanings += AmbiguousWord.split_by_parts_of_speech(raw_meaning)

        for raw_meaning in fixed_meanings:
            meaning = Meaning(*raw_meaning)
            self.meanings.append(meaning)

    def __str__(self):
        _str = "word: {0}, meanings: [".format(self.word)
        for meaning in self.meanings:
            _str += str(meaning) + ", "
        return _str + "]"

    noun_types = {"subst", "ger", "depr"}

    def all_tags(self) -> List[List[str]]:
        """Returns list of tags from every possible meaning of word"""
        tags = []
        for meaning in self.meanings:
            tags += meaning.unfiltered_tags
        return tags

    @staticmethod
    def get_parts_of_speech_from_meaning(meaning: Tuple[str, str, Tuple]) -> Set[str]:
        """Returns parts of speect occuring in raw list of meanings"""
        tags = meaning[2]
        parts_of_speech = {tag.split(":")[0] for tag in tags}
        return parts_of_speech

    @staticmethod
    def split_by_parts_of_speech(meaning: Tuple[str, str, Tuple]) -> List[Tuple[str, str, Tuple]]:
        """Splits raw meaning into list of raw meanings,
        where each tag of each meaning has exactly one part of speech"""

        def get_tags_with_given_part_of_speech(pos) -> List[str]:
            tags = []
            for tag in meaning[2]:
                if tag.split(":")[0] == pos:
                    tags.append(tag)
            return tags

        parts_of_speech = AmbiguousWord.get_parts_of_speech_from_meaning(meaning)
        if len(parts_of_speech) == 1:
            return [meaning]

        word, base_word, _ = meaning
        splitted_meanings = []
        for part_of_speech in parts_of_speech:
            classified_tags = get_tags_with_given_part_of_speech(part_of_speech)
            splitted_meanings.append((word, base_word, tuple(classified_tags)))
        return splitted_meanings

    def parts_of_speech(self) -> Set[str]:
        """Returns part of speech of every stored meaning of ambiguous word"""
        return {meaning.part_of_speech for meaning in self.meanings}


class Morphosyntactic:
    def __init__(self, dictionary_file_path):
        self.morphosyntactic_dictionary = defaultdict(lambda: [])
        self.dictionary_file_path = dictionary_file_path

    def create_morphosyntactic_dictionary(self):
        with open(self.dictionary_file_path, 'r', encoding='utf-8') as file:
            print("+++ creating morphosyntactic dictionary +++")
            print_progress = progress_bar()
            for line_number, line in enumerate(file.readlines()):
                if line_number % 1000 == 0:
                    progress = line_number / DICT_LEN
                    print_progress(progress)
                base_word, word, tags = line.rstrip("\n").split(";")
                tags = tuple(tags.split("+"))
                self.morphosyntactic_dictionary[word.lower()].append((word, base_word, tags))
            print("\n+++ morphosyntactic dictionary created +++")
        return self.morphosyntactic_dictionary

if __name__ == "__main__":
    morph = Morphosyntactic("polimorfologik-2.1.txt")
    print(Meaning.fix_tags(['ger:sg:nom.acc:n2:imperf:aff:refl.nonrefl']))
    assert Meaning.fix_tags(['ger:sg:nom.acc:n2:imperf:aff:refl.nonrefl']) == [
        'ger:sg:nom:n2:imperf:aff:refl.nonrefl'.split(":"),
        'ger:sg:acc:n2:imperf:aff:refl.nonrefl'.split(":")
    ]
    morph.create_morphosyntactic_dictionary()
    d = morph.morphosyntactic_dictionary
    print(d["pić"])
    print(d["piła"])
    print(d["picie"])
    assert d["pić"] == [('pić', 'picie', ('subst:pl:gen:n2',)),
                        ('pić', 'pić', ('verb:inf:imperf:refl.nonrefl',))]
    assert d["picie"] == [('Picie', 'PIT', ('subst:sg:loc:m3', 'subst:sg:voc:m3')),
                          ('picie', 'picie', ('subst:sg:acc:n2', 'subst:sg:nom:n2', 'subst:sg:voc:n2')),
                          ('picie', 'pita', ('subst:sg:dat:f', 'subst:sg:loc:f')),
                          ('picie', 'pić', ('ger:sg:nom.acc:n2:imperf:aff:refl.nonrefl',))]

    sample_meaning = AmbiguousWord("pić", d["pić"]).meanings[0]
    print(sample_meaning)
    assert ['subst', 'pl', 'gen', 'n2'] in sample_meaning.unfiltered_tags
    sample_word = AmbiguousWord("picie", d["picie"])
    print(sample_word)
    assert "pita" in [meaning.base_word for meaning in sample_word.meanings]
    assert [
               ['subst', 'sg', 'dat', 'f'],
               ['subst', 'sg', 'loc', 'f']
           ] in [meaning.unfiltered_tags for meaning in sample_word.meanings]
    sample_raw_meaning = ('pić', 'picie', ('subst:pl:gen:n2',))
    sample_raw_mixed_meaning = (
        'czerwony', 'czerwony',
        ('adj:sg:acc:m3:pos', 'adj:sg:nom.voc:m1.m2.m3:pos', 'subst:sg:nom:m1', 'subst:sg:voc:m1'))
    print(AmbiguousWord.get_parts_of_speech_from_meaning(sample_raw_mixed_meaning))
    assert AmbiguousWord.get_parts_of_speech_from_meaning(sample_raw_mixed_meaning) == {"adj", "subst"}
    assert AmbiguousWord.split_by_parts_of_speech(sample_raw_meaning) == [sample_raw_meaning]
    print(AmbiguousWord.split_by_parts_of_speech(sample_raw_mixed_meaning))
    print(AmbiguousWord.split_by_parts_of_speech(sample_raw_mixed_meaning)[0][-1])
    assert set(AmbiguousWord.split_by_parts_of_speech(sample_raw_mixed_meaning)) == {
        ('czerwony', 'czerwony', ('adj:sg:acc:m3:pos', 'adj:sg:nom.voc:m1.m2.m3:pos')),
        ('czerwony', 'czerwony', ('subst:sg:nom:m1', 'subst:sg:voc:m1'))
    }
    print(Meaning(*sample_raw_meaning).part_of_speech)
    assert Meaning(*sample_raw_meaning).part_of_speech == "subst"

    tricky_word = AmbiguousWord("czerwony", [sample_raw_mixed_meaning])
    print(tricky_word)
    assert tricky_word.parts_of_speech() == {"adj", "subst"}
    assert {meaning.base_word for meaning in tricky_word.meanings} == {"czerwony"}
