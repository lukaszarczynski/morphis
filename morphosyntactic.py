from collections import defaultdict
import sys

CONSOLE_WIDTH = 80


def progress_bar(console_width=CONSOLE_WIDTH):
    already_printed = 0

    def print_progress(progress):
        nonlocal already_printed
        if progress >= already_printed / console_width:
            print("=", end='')
            sys.stdout.flush()
            already_printed += 1
    return print_progress


class Morphosyntactic:
    def __init__(self, dictionary_file_path):
        self.morphosyntactic_dictionary = defaultdict(lambda: [])
        self.dictionary_file_path = dictionary_file_path

    def create_morphosyntactic_dictionary(self):
        with open(self.dictionary_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            dictionary_length = len(lines)
            print("+++ creating morphosyntactic dictionary +++")
            print(" " * (CONSOLE_WIDTH-1), "|")
            print_progress = progress_bar()
            for line_number, line in enumerate(lines):
                if line_number % 1000 == 0:
                    progress = line_number / dictionary_length
                    print_progress(progress)
                base_word, word, tags = line.rstrip("\n").split(";")
                tags = tuple(tags.split("+"))
                self.morphosyntactic_dictionary[word].append((base_word, tags))
            print("\n+++ morphosyntactic dictionary created +++")
        return self.morphosyntactic_dictionary

if __name__ == "__main__":
    morph = Morphosyntactic("polimorfologik-2.1.txt")
    morph.create_morphosyntactic_dictionary()
    d = morph.morphosyntactic_dictionary
    print(d["pić"])
    print(d["piła"])
    print(d["picie"])
    assert d["pić"] == [('picie', ('subst:pl:gen:n2',)), ('pić', ('verb:inf:imperf:refl.nonrefl',))]
    assert d["picie"] == [('picie', ('subst:sg:acc:n2', 'subst:sg:nom:n2', 'subst:sg:voc:n2')),
                          ('pita', ('subst:sg:dat:f', 'subst:sg:loc:f')),
                          ('pić', ('ger:sg:nom.acc:n2:imperf:aff:refl.nonrefl',))]
