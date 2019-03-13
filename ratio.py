import re

import pandas as pd
from nomenclature_parser.pattern_parser import get_nomenclature_item_characteristics

ITEM_NAME = "name"
PRODUCER = "producer"
MODEL = "model"
DESTINATION = "destination"
TYPE = "type"
MATERIAL = "material"
COLOR = "color"
SIZE = "size"
WEIGHT = "weight"
PHYSICS = "physics"
ADDITIONAL = "packaging"
OTHER = "other"

CHAR_REPLACEMENTS = {}
CHAR_REPLACEMENTS[PRODUCER] = [MODEL]
CHAR_REPLACEMENTS[MODEL] = [TYPE, DESTINATION, SIZE, PRODUCER, MATERIAL, COLOR]
CHAR_REPLACEMENTS[DESTINATION] = [TYPE, MODEL, ITEM_NAME]
CHAR_REPLACEMENTS[TYPE] = [DESTINATION, SIZE, MATERIAL, COLOR, MODEL]
CHAR_REPLACEMENTS[MATERIAL] = [TYPE, COLOR, MODEL, DESTINATION]
CHAR_REPLACEMENTS[COLOR] = [TYPE, MATERIAL, MODEL, SIZE]
CHAR_REPLACEMENTS[SIZE] = [WEIGHT, PHYSICS, TYPE, MODEL, ADDITIONAL]
CHAR_REPLACEMENTS[WEIGHT] = [SIZE, PHYSICS, ADDITIONAL]
CHAR_REPLACEMENTS[PHYSICS] = [WEIGHT, SIZE, MODEL, TYPE, ADDITIONAL]
CHAR_REPLACEMENTS[ADDITIONAL] = [WEIGHT, SIZE, PHYSICS, MODEL, TYPE]
CHAR_REPLACEMENTS[OTHER] = []

characteristics = {
        "Выделенное имя": "name",
        "Производитель/ Бренд": "producer",
        "Модель/ Партномер/ Название/ ГОСТ(Стандарт)": "model",
        "Назначение/ Принадлженость": "destination",
        "Классификатор": "model",
        "Тип/ Исполнение/ Конструкция/ Разновидность": "type",
        "Материал\n(Выбор из списка)": "material",
        "Цвет (Выбор из списка)": "color",
        "Размеры": "size",
        "Вес/Объем": "weight",
        "Физическая величина": "physics",
        "Доп признак:\n- Количество/Количество в упаковке": "packaging"
    }

def find_char_replacement(char, item):
    item_characteristics = get_nomenclature_item_characteristics(item)
    normalized_chars = [characteristics[k] for k in item_characteristics]
    if char in normalized_chars:
        return char
    else:
        for another in CHAR_REPLACEMENTS[char]:
            if another in normalized_chars:
                return another

    return None

def key(name, word):
    return "{}\t{}".format(name, word)

def evaluate_accuracy_ratio2(parsed_nomenclature_file, test_nomenclature_file):
    parsed_nomenclature = pd.read_excel(parsed_nomenclature_file).dropna(how="all").fillna("")
    test_nomenclature = pd.read_excel(test_nomenclature_file).dropna(how="all").fillna("").drop_duplicates()

    nomenclature = pd.read_excel("nomenclature.xlsx")
    nomenclature_patterns = pd.read_excel("nomenclature_patterns.xlsx")

    # Join nomenclature dataframe and nomenclature patterns dataframe on column "Наименование целевого ОЗМ"
    nomenclature_characteristic = nomenclature.join(nomenclature_patterns.set_index("Наименование целевого ОЗМ"),
                                                    on="Наименование целевого ОЗМ")

    labeled_names = []
    pair_to_result = {}

    for index, row in test_nomenclature.iterrows():
        if not row.empty:
            labeled_names.append(row['INPUT:text'])
            k = key(row['INPUT:text'], row['INPUT:part'])
            if k not in pair_to_result:
                pair_to_result[k] = []

            result_char = row['OUTPUT:characteristic']
            s = nomenclature_characteristic.loc[
                nomenclature_characteristic['Наименование ТМЦ'] == row['INPUT:text']]
            if not s.empty:
                pair_to_result[k].append(find_char_replacement(result_char, s.iloc[0]))
            else:
                pair_to_result[k].append(result_char)

    labeled_names = set(labeled_names)
    print("Number of labeled items: {}".format(len(labeled_names)))

    all_lines = 0
    matched_lines = 0

    all_chars = 0
    matched_chars = 0

    all_words = 0
    mathed_words = 0

    for index, row in parsed_nomenclature.iterrows():
        name = row['Наименование ТМЦ']
        for column in characteristics.keys():
            result_words = row[column].split(' ')
            for w in result_words:
                k = key(name, w)
                if k in pair_to_result:
                    all_words += 1
                    if characteristics[column] in pair_to_result[k]:
                        mathed_words += 1

    print("By word accuracy: {}".format(mathed_words / all_words))




def evaluate_accuracy_ratio(parsed_nomenclature_file, test_nomenclature_file):
    parsed_nomenclature = pd.read_excel(parsed_nomenclature_file).dropna(how="all").fillna("")
    test_nomenclature = pd.read_excel(test_nomenclature_file).dropna(how="all").fillna("").drop_duplicates()
    characteristics = {
        "Выделенное имя": "name",
        "Производитель/ Бренд": "producer",
        "Модель/ Партномер/ Название/ ГОСТ(Стандарт)": "model",
        "Назначение/ Принадлженость": "destination",
        "Классификатор": "model",
        "Тип/ Исполнение/ Конструкция/ Разновидность": "type",
        "Материал\n(Выбор из списка)": "material",
        "Цвет (Выбор из списка)": "color",
        "Размеры": "size",
        "Вес/Объем": "weight",
        "Физическая величина": "physics",
        "Доп признак:\n- Количество/Количество в упаковке": "packaging"
    }

    total_count = 0
    parsed_count = 0

    for index, row in parsed_nomenclature.iterrows():
        test_rows = test_nomenclature.loc[test_nomenclature["INPUT:text"] == row["Наименование ТМЦ"]]
        if not test_rows.empty:
            for column in characteristics.keys():
                if row[column] != "" and row[column] is not None:
                    test_cells = test_rows.loc[test_nomenclature["OUTPUT:characteristic"] == characteristics[column]][
                        "INPUT:part"]
                    if not test_cells.empty:
                        parsed_values = list(filter(None, re.split(r' |\n|;|\\(|\\)', row[column])))

                        test_values = []
                        for test_cell in test_cells:
                            if test_cell != "" and test_cell is not None:
                                test_values += list(filter(None, re.split(r' |\n|;|\\(|\\)', str(test_cell))))

                        total_count += 1
                        for parsed_value in parsed_values:
                            if any(test_value == parsed_value for test_value in test_values if
                                   test_value is not None and test_value != ""):
                                parsed_count += 1
                                break

    return parsed_count / total_count
