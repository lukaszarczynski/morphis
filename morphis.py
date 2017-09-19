import math
from os.path import isfile
from decimal import Decimal
import decimal
from typing import List

import tokenization
import morphosyntactic


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
    else:
        print("Nawet się nie starasz...")

def read_copypasta() -> List[str]:
    """Reads copypasta from input or from file, returns arrays of tokens and non-alphanumeric strings"""
    print("\nPrzeciągnij plik z pastą do tego okna lub wklej tu pastę\n")

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
            pasta = "".join(file.readlines())
    else:
        pasta = "\n".join(lines)

    pasta = tokenization.tokenize(pasta)
    return pasta


def find_morphosyntactic() -> str:
    """Finds file with morphosyntactic dictionary"""
    if isfile("polimorfologik-2.1.txt"):
        return "polimorfologik-2.1.txt"
    else:
        path = ""
        while not isfile(path):
            print("Pobierz słownik morfosyntaktyczny\n"
                  "https://github.com/morfologik/polimorfologik/releases/tag/2.1\n"
                  "i podaj ścieżkę do niego")
            path = input().rstrip("\n").strip('"')
        return path


if __name__ == "__main__":
    are_you_human()
    morph_path = find_morphosyntactic()
    morph = morphosyntactic.Morphosyntactic(morph_path)
    morph.create_morphosyntactic_dictionary()

    pasta = read_copypasta()
    print(pasta)
    for token in pasta:
        if token.isalnum():
            print(token, "=>", morph.morphosyntactic_dictionary[token])