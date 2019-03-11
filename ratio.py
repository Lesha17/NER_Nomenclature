import re

import pandas as pd


def evaluate_accuracy_ratio(parsed_nomenclature_file, test_nomenclature_file):
    parsed_nomenclature = pd.read_excel(parsed_nomenclature_file).dropna(how="all").fillna("")
    test_nomenclature = pd.read_excel(test_nomenclature_file).dropna(how="all").fillna("").drop_duplicates()
    characteristics = {
        "Производитель/ Бренд": "producer",
        "Модель/ Партномер/ Название/ ГОСТ(Стандарт)": "name",
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
                        for parsed_value in parsed_values:
                            print(parsed_value)
                        print("---")

                        test_values = []
                        for test_cell in test_cells:
                            if test_cell != "" and test_cell is not None:
                                test_values += list(filter(None, re.split(r' |\n|;|\\(|\\)', str(test_cell))))
                        for test_value in test_values:
                            print(test_value)

                        total_count += 1
                        for parsed_value in parsed_values:
                            if any(test_value == parsed_value for test_value in test_values if
                                   test_value is not None and test_value != ""):
                                parsed_count += 1
                                break
                    else:
                        print("empty")
                    print("---------------")

    return parsed_count / total_count