from collections import namedtuple
from enum import Enum


class Gender(Enum):
    MASCULINE_HUMAN = 0
    MASCULINE_ANIMATE = 1
    MASCULINE_INANIMATE = 2
    FEMININE = 3
    NEUTER = 4


class Aspect(Enum):
    IMPERFECTIVE = 0
    PERFECTIVE = 1
    BOTH = 2


class Number(Enum):
    SINGULAR = 0
    PLURAL = 1


class Case(Enum):
    NOMINATIVE = 0
    GENITIVE = 1
    DATIVE = 2
    ACCUSATIVE = 3
    INSTRUMENTAL = 4
    LOCATIVE = 5
    VOCATIVE = 6


Declension = namedtuple(typename="Declension", field_names="number case")

gender_abbreviations = {
    "m1": Gender.MASCULINE_HUMAN,
    "m2": Gender.MASCULINE_ANIMATE,
    "m3": Gender.MASCULINE_INANIMATE,
    "f": Gender.FEMININE,
    "n": Gender.NEUTER,
    "n1": Gender.NEUTER,
    "n2": Gender.NEUTER
}

aspect_abbreviations = {
    "imperf": Aspect.IMPERFECTIVE,
    "perf": Aspect.PERFECTIVE,
    "imperf.perf": Aspect.BOTH
}

number_abbreviations = {
    "sg": Number.SINGULAR,
    "pl": Number.PLURAL
}

case_abbreviations = {
    "nom": Case.NOMINATIVE,
    "gen": Case.GENITIVE,
    "dat": Case.DATIVE,
    "acc": Case.ACCUSATIVE,
    "inst": Case.INSTRUMENTAL,
    "loc": Case.LOCATIVE,
    "voc": Case.VOCATIVE
}

case_to_questions = {
    "nom": "miejscownik (kto?, co?)",
    "gen": "dopełniacz (kogo?, czego?)",
    "dat": "celownik (komu?, czemu?)",
    "acc": "biernik (kogo? co?)",
    "inst": "narzędnik (z kim? z czym?)",
    "loc": "miejscownik (o kim?, o czym?)",
    "voc": "wołacz (ty Janie _)"
}

gender_examples = {
    "m1": "męski, osobowy (np. papież)",
    "m2": "męski, ożywiony (np. mamut)",
    "m3": "męski, nieożywiony (np. melon)",
    "f": "żeński",
    "n": "nijaki"
}

cases_order = ["nom", "gen", "dat", "acc", "inst", "loc", "voc"]
