from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *

import pandas as pd

from nomenclature_parser.machine_learning_dictionary import create_word_dictionary, save_dict, load_dict
from nomenclature_parser.pattern_parser import parse_nomenclature


class NomenclatureParserUI(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("NomenclatureParser")

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

        # self.status = Label(self, text="")
        self._status = StringVar(self)
        self.status = Label(self, textvariable=self._status)
        self.status.grid(row=4, columnspan=3)

        self._progress_bar_value = IntVar()
        self._progress_bar_value.set(0)
        self._progress_bar_max_value = IntVar()
        self._progress_bar_max_value.set(0)

        self.progress_bar = Progressbar(self, variable=self._progress_bar_value, maximum=0)
        self.progress_bar.grid(row=5, columnspan=3)

    def start_parsing(self):
        if self._nomenclature_file_path is not None and self._nomenclature_patterns_file_path is not None:
            nomenclature = pd.read_excel(self._nomenclature_file_path)
            nomenclature_patterns = pd.read_excel(self._nomenclature_patterns_file_path)

            main_split_pattern = ' |\n|;|\\(|\\)'
            split_patterns = [main_split_pattern]

            dictFile = 'dict.txt'

            if os.path.isfile(dictFile):
                self.progress_bar.configure(maximum=3)
                self._set_status("Загружаем словарь данных")
                word_dictionary = load_dict(dictFile)
                self._increase_progress_bar()

                print("Loaded dictionary from {}".format(dictFile))
            else:
                self.progress_bar.configure(maximum=4)
                print("Creating dictionary")
                word_dictionary = set()
                self._set_status("Создаем словарь данных")
                for split_pattern in split_patterns:
                    print("Splitting using pattern {}".format(split_pattern))

                    result_dict = create_word_dictionary(nomenclature, nomenclature_patterns, split_pattern)

                    print("Size of dict: {}".format(len(result_dict)))
                    word_dictionary = word_dictionary.union(result_dict)
                self._increase_progress_bar()
                print("Dictionary size: {}".format(len(word_dictionary)))

                self._set_status("Сохраняем словарь данных")
                save_dict(word_dictionary, dictFile)
                self._increase_progress_bar()

            self._set_status("Распознаем номенклатуру")
            parsed_nomenclature = parse_nomenclature(split_patterns, list(word_dictionary))
            self._increase_progress_bar()

            self._set_status("Сохраняем номенклатуру")
            parsed_nomenclature.to_excel("parsed_nomenclature.xlsx")
            self._increase_progress_bar()

            self._set_status("Готово")

    def _get_nomenclature_file_path(self):
        self._nomenclature_file_path = self._get_file()

    def _get_nomenclature_patterns_file_path(self):
        self._nomenclature_patterns_file_path = self._get_file()

    @staticmethod
    def _get_file():
        file_path = askopenfilename(filetypes=[("Excel", "*.xlsx")])
        return file_path

    def _set_status(self, status):
        self._status.set(status)
        self.update()

    def _increase_progress_bar(self):
        self._progress_bar_value.set(self._progress_bar_value.get() + 1)
        self.update()

    _nomenclature_file_path = "./nomenclature.xlsx"
    _nomenclature_patterns_file_path = "./nomenclature_patterns.xlsx"
    _split_pattern = " |\n|;|\\(|\\)"
