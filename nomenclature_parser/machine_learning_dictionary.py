import re


def split_string(string, split_pattern):
    return re.split(split_pattern, str(string))


def create_word_dictionary(nomenclature, nomenclature_patterns, split_pattern):
    nomenclature_characteristics = nomenclature.join(nomenclature_patterns.set_index("Наименование целевого ОЗМ"),
                                                     on="Наименование целевого ОЗМ")

    columns = nomenclature_characteristics.columns

    dictionary = set()
    for index, item in nomenclature_characteristics.iterrows():
        for column in columns:
            dictionary = dictionary.union(set(split_string(item[column], split_pattern)))

    return dictionary
