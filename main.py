import pandas as pd
import os

from nomenclature_parser.machine_learning_dictionary import create_word_dictionary, save_dict, load_dict
from nomenclature_parser.pattern_parser import parse_nomenclature
from ui.NomenclatureParserUI import NomenclatureParserUI

split_pattern = ' |\n|;|\\(|\\)'
nomenclature = pd.read_excel("nomenclature.xlsx")
nomenclature = nomenclature.append(pd.read_excel("nomenclature2.xlsx"), ignore_index=True)
nomenclature_patterns = pd.read_excel("nomenclature_patterns.xlsx")

main_split_pattern = ' |\n|;|\\(|\\)'
split_patterns = [main_split_pattern]

dictFile = 'dict.txt'

NomenclatureParserUI().mainloop()

# if os.path.isfile(dictFile):
#     word_dictionary = load_dict(dictFile)
#     print("Loaded dictionary from {}".format(dictFile))
# else:
#     print("Creating dictionary")
#     word_dictionary = set()
#     for split_pattern in split_patterns:
#         print("Splitting using pattern {}".format(split_pattern))
#         result_dict = create_word_dictionary(nomenclature, nomenclature_patterns, split_pattern)
#         print("Size of dict: {}".format(len(result_dict)))
#         word_dictionary = word_dictionary.union(result_dict)
#     print("Dictionary size: {}".format(len(word_dictionary)))
#     save_dict(word_dictionary, dictFile)
#
# parsed_nomenclature = parse_nomenclature(split_patterns, list(word_dictionary))
# parsed_nomenclature.to_excel("parsed_nomenclature.xlsx")
