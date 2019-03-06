import pandas as pd

from nomenclature_parser.fuzzy_logic import fuzzy_logic
from nomenclature_parser.machine_learning_dictionary import create_word_dictionary
from nomenclature_parser.pattern_parser import parse_nomenclature

split_pattern = ' |\n|;|,|\\(|\\)'
nomenclature = pd.read_excel("nomenclature.xlsx")
nomenclature = nomenclature.append(pd.read_excel("nomenclature2.xlsx"))
nomenclature_patterns = pd.read_excel("nomenclature_patterns.xlsx")

word_dictionary = create_word_dictionary(nomenclature, nomenclature_patterns, split_pattern)
dataframes, word2pc, word2predict, cntr = fuzzy_logic(word_dictionary)
parsed_nomenclature = parse_nomenclature(split_pattern, word2pc, word2predict, cntr)

parsed_nomenclature.to_excel("parsed_nomenclature.xlsx")
