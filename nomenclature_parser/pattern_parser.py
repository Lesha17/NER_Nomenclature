from math import sqrt

import pandas as pd
import numpy as np
import skfuzzy

from nomenclature_parser.Match import *
from nomenclature_parser.WordsTuple import *
from nomenclature_parser.fuzzy_logic import predict
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
        if item[characteristic] not in EMPTY:
            ic = str(item[characteristic])

            # Matches strings "из списка", "список"
            if "спис" in ic.lower():
                item[characteristic] = ic.split("\n")[1:]
            elif "ручной ввод" in ic.lower():
                item[characteristic] = ic.split("\n")[2:]  # "ручной ввод"
            else:
                item[characteristic] = [item[characteristic]]
            # TODO: find the way to parse Модель/ Партномер/ Название/ ГОСТ(Стандарт) and Производитель/ Бренд columns

            item_characteristics[characteristic] = item[characteristic]
        if ADDITIONAL in item_characteristics:
            item_characteristics[ADDITIONAL].append(item['БЕИ'])
            item_characteristics[ADDITIONAL].append(item['АЕИ'])

        item_characteristics[ITEM_NAME] = [item['Наименование целевого ОЗМ']]

    return item_characteristics


def match(t1, t2, cntr):
    if len(t1.words) == len(t2.words):
        deltaSum = 0.0
        for i in range(len(t1.words)):
            delta = np.linalg.norm(t2.predicts[i] - t1.predicts[i])
            deltaSum = deltaSum + delta ** 2
        delta = np.sqrt(deltaSum / len(t1.words))
    else:
        sum1 = np.asarray([0] * t1.pcs[0].shape[0])
        for v in t1.pcs:
            sum1 = sum1 + v
        sum1 = sum1 / len(t1.pcs)

        sum2 = np.asarray([0] * t2.pcs[0].shape[0])
        for v in t2.pcs:
            sum2 = sum2 + v
        sum2 = sum2 / len(t2.pcs)

        predict1 = predict(sum1, cntr)
        predict2 = predict(sum2, cntr)

        delta = np.linalg.norm(predict2 - predict1)

    return Match(t1, t2, delta)


def matches_with_common(common_predicts, t, cntr):
    matches = []
    for cp in common_predicts:
        delta = np.linalg.norm(cp - t.total_predict(cntr))
        m = Match(t, WordsTuple(), delta)
        matches.append(m)
    return matches


max_tuple_size = 2


def word_tuples(line, word2pc, word2predict, split_pattern):
    words = split_string(line, split_pattern)
    words = [w for w in words if w not in EMPTY]
    tuples = []
    for i in range(len(words)):
        for j in range(i + 1, min(i + max_tuple_size + 1, len(words) + 1)):
            t = WordsTuple()
            t.words = words[i:j]
            for w in t.words:
                pc = word2pc[w]
                predict = word2predict[w]
                t.pcs.append(pc)
                t.predicts.append(predict)
            tuples.append(t)
    return tuples


def parse_nomenclature(split_pattern, word2pc, word2predict, cntr):
    common_characteristics = {}
    for index, item in nomenclature_characteristic.iterrows():
        itemCharacteristics = get_nomenclature_item_characteristics(item)

        for k, vals in itemCharacteristics.items():
            if k not in common_characteristics:
                common_characteristics[k] = []
            for v in vals:
                if v in EMPTY:
                    continue
                itemTuples = word_tuples(v, word2pc, word2predict, split_pattern)
                common_characteristics[k] += itemTuples

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
        vector_array = [t.total_predict(cntr) for t in c]
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

    for k, c in common_characteristics.items():
        avrg_pcs = np.asarray([0] * c[0].pcs[0].shape[0])
        avrg_predict = np.asarray([0] * c[0].predicts[0].shape[0])
        avrg_total_predict = np.asarray([0] * c[0].predicts[0].shape[0])

        for t in c:
            t_pcs = t.avrg_pcs()
            t_predict = t.avrg_predict()
            t_total_predict = t.total_predict(cntr)

            avrg_pcs = avrg_pcs + t_pcs
            avrg_predict = avrg_predict + t_predict
            avrg_total_predict = avrg_total_predict + t_total_predict

        avrg_pcs = avrg_pcs / len(c)
        avrg_predict = avrg_predict / len(c)
        avrg_total_predict = avrg_total_predict / len(c)
        avrg_pcs_predict = predict(avrg_pcs, cntr)

        pcs_mse = 0
        predict_mse = 0
        total_predict_mse = 0
        avrg_pcs_predict_mse = 0

        for t in c:
            pcs_mse += np.linalg.norm(avrg_pcs - t.avrg_pcs()) ** 2
            predict_mse += np.linalg.norm(avrg_predict - t.avrg_predict()) ** 2
            total_predict_mse += np.linalg.norm(avrg_total_predict - t.total_predict(cntr)) ** 2
            avrg_pcs_predict_mse += np.linalg.norm(avrg_pcs_predict - t.total_predict(cntr)) ** 2

        pcs_mse = sqrt(pcs_mse / len(c))
        predict_mse = sqrt(predict_mse / len(c))
        total_predict_mse = sqrt(total_predict_mse / len(c))
        avrg_pcs_predict_mse = sqrt(avrg_pcs_predict_mse / len(c))

    def diff_len(v1, v2):
        s = 0
        return np.linalg.norm(v1 - v2)

    MAX_DELTA = 0.4

    def parse_nomenclature_item_characteristics(item, item_characteristics):
        parsed_characteristics = {}

        item_word_tuples = word_tuples(item, word2pc, word2predict, split_pattern)

        matches = []
        for it in item_word_tuples:
            for k, c in item_characteristics.items():
                common_matches = matches_with_common(common_characteristics_clusters[k], it, cntr)
                for cm in common_matches:
                    cm.key = k
                matches += common_matches

                for v in c:
                    cWordTuples = word_tuples(v, word2pc, word2predict, split_pattern)
                    for ct in cWordTuples:
                        m = match(it, ct, cntr)
                        m.key = k
                        matches.append(m)

        matches.sort(key=lambda x: x.delta)

        while len(matches) > 0:
            m = matches[0]
            if m.delta > MAX_DELTA:
                break

            val = ''
            for w in m.t1.words:
                val += w + ' '
            val = val.strip()

            if m.key in parsed_characteristics:
                parsed_characteristics[m.key] += (' ' + val)
            else:
                parsed_characteristics[m.key] = val

            for w in m.t1.words:
                matches = [m1 for m1 in matches if w not in m1.t1.words]

        #    for item_characteristic in item_caracteristics:
        # TODO: analize item characteristic using machine learning
        # Random generation string with length = 3
        # parsed_characteristic = "".join(
        #     choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(3))
        # parsed_characteristics[item_characteristic] = parsed_characteristic

        return parsed_characteristics

    for index, item in nomenclature_characteristic.head().iterrows():
        itemName = item['Наименование ТМЦ']

        parsed_characteristics = parse_nomenclature_item_characteristics(itemName,
                                                                         get_nomenclature_item_characteristics(item))
    parsed_nomenclature = pd.DataFrame(columns=["Наименование ТМЦ"] + CHARACTERISTICS + [ITEM_NAME])

    for index, item in nomenclature_characteristic.iterrows():
        #    item_characteristics = get_nomenclature_item_characteristics(item)
        itemName = item['Наименование ТМЦ']
        parsed_characteristics = parse_nomenclature_item_characteristics(itemName,
                                                                         get_nomenclature_item_characteristics(item))

        # Fill empty characteristics
        for characteristic in CHARACTERISTICS:
            if characteristic not in parsed_characteristics:
                parsed_characteristics[characteristic] = ""

        # Fill item descriptions
        for description in DESCRIPTIONS:
            parsed_characteristics[description] = item[description]

        parsed_characteristics["Наименование ТМЦ"] = item["Наименование ТМЦ"]

        parsed_nomenclature = parsed_nomenclature.append(parsed_characteristics, ignore_index=True)

    # pcVec1 = pcDict['44х100']
    # pcVec2 = pcDict['Camelion']
    # vecDiff = pcVec1 - pcVec2

    # predict1 = predict(pcVec1, cntr)
    # predict2 = predict(pcVec2, cntr)

    return parsed_nomenclature
