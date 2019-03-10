from math import sqrt

import pandas as pd
import numpy as np
import skfuzzy

from nomenclature_parser.Match import *
from nomenclature_parser.Word import *
from nomenclature_parser.embeds import Embedder
from nomenclature_parser.machine_learning_dictionary import split_string

nomenclature = pd.read_excel("nomenclature.xlsx")
nomenclature_patterns = pd.read_excel("nomenclature_patterns.xlsx")

# Join nomenclature dataframe and nomenclature patterns dataframe on column "Наименование целевого ОЗМ"
nomenclature_characteristic = nomenclature.join(nomenclature_patterns.set_index("Наименование целевого ОЗМ"),
                                                on="Наименование целевого ОЗМ")

CHARACTERISTICS = [
    # "БЕИ",
    # "АЕИ",
    "Производитель/ Бренд",
    "Модель/ Партномер/ Название/ ГОСТ(Стандарт)",
    "Назначение/ Принадлженость",
    "Классификатор",
    "Тип/ Исполнение/ Конструкция/ Разновидность",
    "Материал\n(Выбор из списка)",
    "Цвет (Выбор из списка)",
    "Размеры",
    "Вес/Объем",
    "Физическая величина",
    "Доп признак:\n- Количество/Количество в упаковке"
]

DESCRIPTIONS = [
    "Код",
    "Наименование ТМЦ",
    "Ед. изм.",
    "Наименование целевого ОЗМ"
]

EMPTY = ["-", "", None]
ADDITIONAL = 'Доп признак:\n- Количество/Количество в упаковке'
ITEM_NAME = 'Выделенное имя'


def get_nomenclature_item_characteristics(item):
    item_characteristics = {}

    for characteristic in CHARACTERISTICS:
        if item[characteristic] not in EMPTY and not pd.isna(item[characteristic]):
            ic = str(item[characteristic])
            vals = []

            # Matches strings "из списка", "список"
            if "спис" in ic.lower():
                vals = ic.split("\n")[1:]
            elif "ручной ввод" in ic.lower():
                vals = ic.split("\n")[2:]  # "ручной ввод"
            else:
                vals = [item[characteristic]]
            # TODO: find the way to parse Модель/ Партномер/ Название/ ГОСТ(Стандарт) and Производитель/ Бренд columns

            item_characteristics[characteristic] = vals
        if ADDITIONAL in item_characteristics:
            item_characteristics[ADDITIONAL].append(item['БЕИ'])
            item_characteristics[ADDITIONAL].append(item['АЕИ'])

        item_characteristics[ITEM_NAME] = [item['Наименование целевого ОЗМ']]

    return item_characteristics


def match(k, w1, w2):
    return Match(w1, w2, k, np.linalg.norm(w1.embed - w2.embed))


def matches_with_common(w, common_embeds, k):
    matches = []
    for e in common_embeds:
        delta = np.linalg.norm(e - w.embed)
        m = Match(w, Word("common#" + k, e), k, delta)
        matches.append(m)
    return matches


max_tuple_size = 2

def get_words(line, embedder, split_patterns):
    words_str = set()
    for split_pattern in split_patterns:
        words_str = words_str.union(split_string(line, split_pattern))
    if '' in words_str:
        words_str.remove('')

    words = [Word(w, embedder.embed(w)) for w in words_str]
    return words


def parse_nomenclature(split_patterns, dictionary):
    embed_dim = 2

    embedder = Embedder(dictionary, embed_dim)

    print("Creating common characteristics embeds")
    common_characteristics = {}
    for index, item in nomenclature_characteristic.iterrows():
        itemCharacteristics = get_nomenclature_item_characteristics(item)

        for k, vals in itemCharacteristics.items():
            if k not in common_characteristics:
                common_characteristics[k] = []
            for v in vals:
                if v in EMPTY:
                    continue
                itemWords = get_words(v, embedder, split_patterns)
                common_characteristics[k] += itemWords

    avrg_fpc = 0
    fpcs = []

    c2ncl = {}

    # Подбираем так, чтобы  был мин. fpc
    # при этом смотрим на mse, если он и так > 90, то 1 кластера достаточно

    c2ncl["Производитель/ Бренд"] = 4  # Done
    c2ncl["Модель/ Партномер/ Название/ ГОСТ(Стандарт)"] = 2  # Done
    c2ncl["Назначение/ Принадлженость"] = 50  # Done
    c2ncl["Классификатор"] = 2  # Done
    c2ncl["Тип/ Исполнение/ Конструкция/ Разновидность"] = 1  # Done
    c2ncl["Материал\n(Выбор из списка)"] = 1  # Done
    c2ncl["Цвет (Выбор из списка)"] = 10  # Done
    c2ncl["Размеры"] = 2  # Done
    c2ncl["Вес/Объем"] = 2  # Done
    c2ncl["Физическая величина"] = 50  # Done
    c2ncl["Доп признак:\n- Количество/Количество в упаковке"] = 4  # Done
    c2ncl[ITEM_NAME] = 8  # Done

    common_characteristics_clusters = {}

    for k, c in common_characteristics.items():
        vector_array = [w.embed for w in c]
        vector_array = np.asarray(vector_array)
        ncl = c2ncl[k]
        char_cluster_centers, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(vector_array.T, ncl, 2, error=0.005,
                                                                         maxiter=10000,
                                                                         init=None)
        common_characteristics_clusters[k] = []
        for c in char_cluster_centers:
            common_characteristics_clusters[k].append(c)

        avrg_fpc += fpc
        fpcs.append(fpc)

    avrg_fpc = avrg_fpc / len(fpcs)

    fpc_d = 0
    for fpc in fpcs:
        fpc_d += fpc ** 2
    fpc_d = sqrt(fpc_d / len(fpcs))

    def itemIsEmpty(word):
        for sp in split_patterns:
            if word.replace(sp, '') != '':
                return False
        return True

    def parse_nomenclature_item_characteristics(item, item_characteristics, logfile=None):
        parsed_characteristics = {}

        item_words = get_words(item, embedder, split_patterns)

        matches = []
        for w in item_words:
            for k, charValues in item_characteristics.items():
                common_matches = matches_with_common(w, common_characteristics_clusters[k], k)
                matches += common_matches

                for charValue in charValues:
                    charWords = get_words(charValue, embedder, split_patterns)
                    for charWord in charWords:
                        m = match(k, w, charWord)
                        matches.append(m)

        matches.sort(key=lambda x: x.delta)
        matches = [m for m in matches if m.delta <= embedder.MAX_DELTA]

        if logfile:
            logfile.write("Matches for {}: {}\n".format(item, [str(m) for m in matches]))

        i = 0
        words = [w.word for w in item_words]
        while len(matches) > i and len(words) > 0:
            m = matches[i]
            i += 1
            if m.delta > embedder.MAX_DELTA:
                break

            matchWord = m.w1.word
            if matchWord not in words:
                continue

            if m.key in parsed_characteristics:
                parsed_characteristics[m.key] += (' ' + matchWord)
            else:
                parsed_characteristics[m.key] = matchWord

            words.remove(matchWord)

        return parsed_characteristics

    parsed_nomenclature = pd.DataFrame(columns=["Наименование ТМЦ"] + CHARACTERISTICS + [ITEM_NAME])

    print("Parsing nomenclature")
    logfile = open("parsing_log.txt", "w")
    print("Using {} for parsing log.".format(logfile))
    for index, item in nomenclature_characteristic.iterrows():
        #    item_characteristics = get_nomenclature_item_characteristics(item)
        itemName = item['Наименование ТМЦ']
        parsed_characteristics = parse_nomenclature_item_characteristics(itemName,
                                                                         get_nomenclature_item_characteristics(item),
                                                                         logfile)

        # Fill empty characteristics
        for characteristic in CHARACTERISTICS:
            if characteristic not in parsed_characteristics:
                parsed_characteristics[characteristic] = ""

        # Fill item descriptions
        for description in DESCRIPTIONS:
            parsed_characteristics[description] = item[description]

        parsed_characteristics["Наименование ТМЦ"] = item["Наименование ТМЦ"]

        parsed_nomenclature = parsed_nomenclature.append(parsed_characteristics, ignore_index=True)

    logfile.close()
    # pcVec1 = pcDict['44х100']
    # pcVec2 = pcDict['Camelion']
    # vecDiff = pcVec1 - pcVec2

    # predict1 = predict(pcVec1, cntr)
    # predict2 = predict(pcVec2, cntr)

    return parsed_nomenclature
