from tkinter import *
from tkinter.filedialog import *

import pandas as pd

from nomenclature_parser.machine_learning_dictionary import create_word_dictionary, save_dict, load_dict
from nomenclature_parser.pattern_parser import parse_nomenclature


class NomenclatureParserUI(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.winfo_toplevel().title("NomenclatureParser")

        Label(self, text="Номенклатура") \
            .grid(row=0, pady=4, padx=10, sticky=W)
        Label(self, text="Правила") \
            .grid(row=1, pady=4, padx=10, sticky=W)
        Label(self, text="Спец. символы") \
            .grid(row=2, pady=4, padx=10, sticky=W)

        nomenclature = Label(self, text=self._nomenclature_file_path) \
            .grid(row=0, column=1, pady=4, padx=10, sticky=W)
        Button(self, text="Открыть", command=self._get_nomenclature_file_path) \
            .grid(row=0, column=2, pady=4, padx=10)

        nomenclature_patterns = Label(self, text=self._nomenclature_patterns_file_path) \
            .grid(row=1, column=1, pady=4, padx=10, sticky=W)
        Button(self, text="Открыть", command=self._get_nomenclature_patterns_file_path) \
            .grid(row=1, column=2, pady=4, padx=10)

        split_pattern = Entry(self)
        split_pattern.grid(row=2, column=1, pady=4, padx=10, columnspan=2, sticky=W)
        split_pattern.insert(END, self._split_pattern)

        Button(self, text="Распознать", command=self.start_parsing) \
            .grid(row=3, column=1, ipady=4, ipadx=16, pady=8, padx=10, sticky=E)

    def start_parsing(self):
        print("here")
        if self._nomenclature_file_path is not None and self._nomenclature_patterns_file_path is not None:
            nomenclature = pd.read_excel(self._nomenclature_file_path)
            nomenclature_patterns = pd.read_excel(self._nomenclature_patterns_file_path)
            # nomenclature = nomenclature.append(pd.read_excel("nomenclature2.xlsx"), ignore_index=True)

            main_split_pattern = ' |\n|;|,|\\(|\\)'
            other_split_patters = [
                ' |-|\n|;|,|\\(|\\)',  # with '-'
                ' |\n|;|,',  # without braces
                ' |-|\n|;|,',  # with '-' without braces
                ' |\n|;|\\(|\\)',  # without comma
                ' |-|\n|;|\\(|\\)',  # with '-' without comma
                ' |\n|;',  # without braces without comma
                ' |-|\n|;'  # with '-' without braces without comma
            ]

            split_patterns = other_split_patters
            split_patterns.append(main_split_pattern)

            dictFile = 'dict.txt'

            if os.path.isfile(dictFile):
                word_dictionary = load_dict(dictFile)
                print("Loaded dictionary from {}".format(dictFile))
            else:
                print("Creating dictionary")
                word_dictionary = set()
                for split_pattern in split_patterns:
                    print("Splitting using pattern {}".format(split_pattern))
                    result_dict = create_word_dictionary(nomenclature, nomenclature_patterns, split_pattern)
                    print("Size of dict: {}".format(len(result_dict)))
                    word_dictionary = word_dictionary.union(result_dict)
                print("Dictionary size: {}".format(len(word_dictionary)))
                save_dict(word_dictionary, dictFile)

            parsed_nomenclature = parse_nomenclature(split_patterns, list(word_dictionary))

            parsed_nomenclature.to_excel("parsed_nomenclature.xlsx")

    def _get_nomenclature_file_path(self):
        self._nomenclature_file_path = self._get_file()

    def _get_nomenclature_patterns_file_path(self):
        self._nomenclature_patterns_file_path = self._get_file()

    @staticmethod
    def _get_file():
        file_path = askopenfilename(filetypes=[("Excel", "*.xlsx")])
        return file_path

    _nomenclature_file_path = "./nomenclature.xlsx"
    _nomenclature_patterns_file_path = "./nomenclature_patterns.xlsx"
    _split_pattern = " |\n|;|\\(|\\)"
