import pandas as pd


def evaluate_accuracy_ratio(parsed_nomenclature_file, test_nomenclature_file):
    parsed_nomenclature = pd.read_excel(parsed_nomenclature_file)
    test_nomenclature = pd.read_excel(test_nomenclature_file)
    total_count = 0.0
    parsed_count = 0.0
    for index, row in test_nomenclature.iterrows():
        parsed_row = parsed_nomenclature.loc[parsed_nomenclature["Наименование ТМЦ"] == row["Наименование ТМЦ"]]
        print(parsed_row)
        for column in test_nomenclature.columns:
            if test_nomenclature[column] is not None and test_nomenclature[column] != "":
                total_count += 1
                if row[column] == parsed_row[column]:
                    parsed_count += 1

    return parsed_count / total_count
