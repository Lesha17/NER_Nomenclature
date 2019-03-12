import pandas as pd
import numpy as np
import math
from sklearn.neighbors import KNeighborsClassifier

from nomenclature_parser.Match import *
from nomenclature_parser.Word import *
from nomenclature_parser.embeds import Embedder
from nomenclature_parser.machine_learning_dictionary import split_string

nomenclature = pd.read_excel("nomenclature.xlsx")
nomenclature_patterns = pd.read_excel("nomenclature_patterns.xlsx")

# Join nomenclature dataframe and nomenclature patterns dataframe on column "Наименование целевого ОЗМ"
nomenclature_characteristic = nomenclature.join(nomenclature_patterns.set_index("Наименование целевого ОЗМ"),
                                                on="Наименование целевого ОЗМ")

ITEM_NAME = "Выделенное имя"
PRODUCER = "Производитель/ Бренд"
MODEL = "Модель/ Партномер/ Название/ ГОСТ(Стандарт)"
DESTINATION = "Назначение/ Принадлженость"
CLASSIFICATOR = "Классификатор"
TYPE = "Тип/ Исполнение/ Конструкция/ Разновидность"
MATERIAL = "Материал\n(Выбор из списка)"
COLOR = "Цвет (Выбор из списка)"
SIZE = "Размеры"
WEIGHT = "Вес/Объем"
PHYSICS = "Физическая величина"
ADDITIONAL = "Доп признак:\n- Количество/Количество в упаковке"


CHARACTERISTICS = [
    # "БЕИ",
    # "АЕИ",
    PRODUCER,
    MODEL,
    DESTINATION,
    CLASSIFICATOR,
    TYPE,
    MATERIAL,
    COLOR,
    SIZE,
    WEIGHT,
    PHYSICS,
    ADDITIONAL
]

DESCRIPTIONS = [
    "Код",
    "Наименование ТМЦ",
    "Ед. изм.",
    "Наименование целевого ОЗМ"
]

EMPTY = ["-", "", None]

CHAR_REPLACEMENTS = {}
CHAR_REPLACEMENTS[PRODUCER] = [MODEL]
CHAR_REPLACEMENTS[MODEL] = [CLASSIFICATOR, TYPE, SIZE, PRODUCER]
CHAR_REPLACEMENTS[DESTINATION] = [TYPE, MODEL, ITEM_NAME]
CHAR_REPLACEMENTS[CLASSIFICATOR] = [MODEL, TYPE, DESTINATION, SIZE, PRODUCER, MATERIAL, COLOR]
CHAR_REPLACEMENTS[TYPE] = [DESTINATION, SIZE, MATERIAL, COLOR, MODEL, CLASSIFICATOR]
CHAR_REPLACEMENTS[MATERIAL] = [TYPE, COLOR, MODEL, DESTINATION]
CHAR_REPLACEMENTS[COLOR] = [TYPE, MATERIAL, MODEL, CLASSIFICATOR, SIZE]
CHAR_REPLACEMENTS[SIZE] = [WEIGHT, PHYSICS, TYPE, MODEL, CLASSIFICATOR, ADDITIONAL]
CHAR_REPLACEMENTS[WEIGHT] = [SIZE, PHYSICS, ADDITIONAL]
CHAR_REPLACEMENTS[PHYSICS] = [WEIGHT, SIZE, MODEL, TYPE, CLASSIFICATOR, ADDITIONAL]
CHAR_REPLACEMENTS[ADDITIONAL] = [WEIGHT, SIZE, PHYSICS, CLASSIFICATOR, MODEL, TYPE]

def get_nomenclature_item_characteristics(item):
    item_characteristics = {}

    for characteristic in CHARACTERISTICS:
        if item[characteristic] not in EMPTY and not pd.isna(item[characteristic]):
            ic = str(item[characteristic])
            vals = [val for val in ic.split("\n") if "спис" not in val.lower() and "прим" not in val.lower()]
            item_characteristics[characteristic] = vals
        if ADDITIONAL in item_characteristics:
            item_characteristics[ADDITIONAL].append(item['БЕИ'])
            item_characteristics[ADDITIONAL].append(item['АЕИ'])

        item_characteristics[ITEM_NAME] = [item['Наименование целевого ОЗМ']]

    return item_characteristics


def match(k, w1, w2):
    return Match(w1, w2, k, np.linalg.norm(w1.embed - w2.embed))


def match_with_common(w, common_classifier, allowed_chars, char_replaces):
    c = common_classifier.predict([w.embed])
    predicted_char = c[0]

    allowed_char = None
    if predicted_char in allowed_chars:
        allowed_char = predicted_char
    else:
        for char_replace in char_replaces[predicted_char]:
            if char_replace in allowed_chars:
                allowed_char = char_replace
                break

    closest_distances, indices = common_classifier.kneighbors([w.embed])
    p = common_classifier.predict_proba([w.embed])
    mean_sq_dist = math.sqrt(np.mean(np.square(closest_distances))) # TODO mean may be better
    delta = mean_sq_dist / (np.max(p[0]) ** 2)
    return Match(w, Word('common#{}->{}'.format(predicted_char, allowed_char), w.embed), allowed_char, delta)


max_tuple_size = 2

def split_to_words(line, split_patterns):
    words_str = set()
    for split_pattern in split_patterns:
        words_str = words_str.union(split_string(line, split_pattern))
    if '' in words_str:
        words_str.remove('')

    return words_str

def get_words(line, embedder, split_patterns):
    words_str = split_to_words(line, split_patterns)

    words = [Word(w, embedder.embed(w)) for w in words_str]
    return words

def create_common_dataset(split_patterns):
    print("Creating common characteristics embeds")

    common_word2char = {}
    common_words = []
    for index, item in nomenclature_characteristic.iterrows():
        itemCharacteristics = get_nomenclature_item_characteristics(item)

        for k, vals in itemCharacteristics.items():
            for v in vals:
                if v in EMPTY:
                    continue
                itemWords = split_to_words(v, split_patterns)
                for w in itemWords:
                    common_word2char[w] = k
                    common_words.append(w)

    dataset = [[w, common_word2char[w]] for w in common_words]
    return dataset

def parse_nomenclature(split_patterns, dictionary):
    embed_dim = 2

    embedder = Embedder(dictionary, embed_dim)

    common_dataset = create_common_dataset(split_patterns)

    common_classifier = KNeighborsClassifier(n_neighbors=5)
    common_classifier.fit([embedder.embed(w[0]) for w in common_dataset], [w[1] for w in common_dataset])

    def parse_nomenclature_item_characteristics(item, item_characteristics, logfile=None):
        parsed_characteristics = {}

        item_words = get_words(item, embedder, split_patterns)

        matches = []
        for w in item_words:
            common_match = match_with_common(w, common_classifier, item_characteristics, CHAR_REPLACEMENTS)
            if common_match.key:
                matches.append(common_match)

            for k, charValues in item_characteristics.items():
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
