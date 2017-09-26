import math
from os.path import isfile
from decimal import Decimal
import decimal
from typing import List, Dict, Tuple

import tokenization
import morphosyntactic
import grammar_category
import replacing

DEBUG = False


def are_you_human():
    """Checks whether user is human or robot"""
    print("Udowodnij, że jesteś człowiekiem\n\n0,1 + 0,2 = ?")
    solution = input().replace(",", ".")
    try:
        solution = Decimal(solution)
    except decimal.InvalidOperation:
        solution = 0
    if solution == Decimal("0.3"):
        print("Dobrze, jesteś człowiekiem")
    elif math.isclose(solution, 0.3, abs_tol=1e-15):
        print("WITAMY W TAJNYM INTERNECIE ROBOTÓW")
        global DEBUG
        DEBUG = True
        replacing.DEBUG = True
    else:
        print("Nawet się nie starasz...")


def read_copypasta() -> List[str]:
    """Reads copypasta from input or from file, returns arrays of tokens and non-alphanumeric strings"""
    print("\nPrzeciągnij plik z pastą do tego okna lub wklej tu pastę (wciśnij 3*Enter, aby zakończyć)\n")

    lines = []
    while True:
        line = input()
        if isfile(line.rstrip("\n").strip('"')):
            lines.append(line)
            break
        elif not line and len(lines) > 0 and not lines[-1]:
            break
        lines.append(line)

    if len(lines) == 1 and isfile(lines[0].rstrip("\n").strip('"')):
        with open(lines[0].rstrip("\n").strip('"')) as file:
            copypasta = "".join(file.readlines())
    else:
        copypasta = "\n".join(lines)

    copypasta = tokenization.tokenize(copypasta)
    return copypasta


def choose_words() -> List[Tuple[Dict, grammar_category.Gender, float]]:
    """Reads replacement words and probability of replacing, for every gender"""
    words = []
    ordered_gender_shortcuts = ["m1", "m2", "m3", "f", "n"]
    for gender in ordered_gender_shortcuts:
        word = {
            grammar_category.Number.SINGULAR: {},
            grammar_category.Number.PLURAL: {}
        }
        print("Podaj rzeczownik rodzaju", grammar_category.gender_examples[gender],
              "lub wciśnij Enter, aby nie zamieniać rzeczowników tego rodzaju")
        input_word = input()
        if not input_word:
            continue
        word[grammar_category.Number.SINGULAR][grammar_category.Case.NOMINATIVE] = input_word
        print("Liczba pojedyncza")
        get_word_cases(word, number=grammar_category.Number.SINGULAR)
        print("Liczba mnoga")
        get_word_cases(word, number=grammar_category.Number.PLURAL)
        probability = -1.
        while probability < 0 or probability > 1:
            probability = float(input("Z jakim prawdopodobieństwem zamienić słowo? [0-1] "))
        words.append((word, grammar_category.gender_abbreviations[gender], probability))
    return words


def get_word_cases(word, *, number):
    """Reads declination of Polish noun, giving hints about Polish cases"""
    for case_shortcut in grammar_category.cases_order:
        case = grammar_category.case_abbreviations[case_shortcut]
        if case in word[number]:
            print(grammar_category.case_to_questions[case_shortcut], ": ", word[number][case])
        else:
            word[number][case] = input(grammar_category.case_to_questions[case_shortcut] + ": ")


def find_morphosyntactic() -> str:
    """Finds file with morphosyntactic dictionary"""
    if isfile("polimorfologik-2.1.txt"):
        return "polimorfologik-2.1.txt"
    else:
        path = ""
        while not isfile(path):
            print("Pobierz słownik morfosyntaktyczny"
                  "https://github.com/morfologik/polimorfologik/releases/tag/2.1"
                  "i podaj ścieżkę do niego", sep="\n")
            path = input().rstrip("\n").strip('"')
        return path


def find_ngrams(n: int) -> str:
    """Find file with n-grams"""
    if isfile("{}grams".format(n)):
        return "{}grams".format(n)
    else:
        path = ""
        while not isfile(path):
            print("Pobierz plik {}grams.gz".format(n),
                  "http://zil.ipipan.waw.pl/NKJPNGrams",
                  "rozpakuj i podaj ścieżkę do pliku {}grams".format(n), sep="\n")
            path = input().rstrip("\n").strip('"')
        return path


if __name__ == "__main__":
    are_you_human()
    morph_path = find_morphosyntactic()
    morph = morphosyntactic.Morphosyntactic(morph_path)
    morph.create_morphosyntactic_dictionary()

    should_continue = True
    while should_continue:
        pasta = read_copypasta()
        if "".join(pasta).strip() == "":
            should_continue = False
            break

        chosen_words = choose_words()  # TODO: Possibility to process many pastas with same chosen words
        if DEBUG:
            print(chosen_words)
        replacer = replacing.Replacing(pasta, chosen_words, morph)
        replaced_pasta = replacer.replace()
        print("".join(replaced_pasta))
