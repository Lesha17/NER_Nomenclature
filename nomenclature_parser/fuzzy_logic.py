import numpy as np
import pandas as pd
import skfuzzy as fuzz
from numpy import array
from sklearn.decomposition import PCA


def encode_word(word, alphabet, char_to_int, onehot_encoded):
    vec = [0] * len(alphabet)
    for c in list(word):
        vec += array(onehot_encoded[char_to_int[c]])
    return vec / np.linalg.norm(vec)


def best_matches(word, word2Predict):
    vals = []
    wordP = word2Predict[word]
    for k, v in word2Predict.items():
        d = np.linalg.norm(wordP - v)
        vals.append([d, k])

    vals.sort(key=lambda x: x[0])


def predict(vec, cntr):
    varr = np.asarray([vec]).T
    u_predict, u0_predict, d_predict, jm_predict, p_predict, fpc_predict = fuzz.cluster.cmeans_predict(varr, cntr, 2,
                                                                                                       error=0.005,
                                                                                                       maxiter=10000)
    return u_predict.T[0]


# text_file = open("output2.txt", "r")
#
# dataset = text_file.read().splitlines()
# dataset = list(filter(None, dataset))
#

def fuzzy_logic(dataset):
    dataset = list(filter(None, dataset))
    # define universe of possible input values
    alphabet = set('')
    for l in dataset:
        alphabet = alphabet.union(set(l))

    # define a mapping of chars to integers
    char_to_int = dict((c, i) for i, c in enumerate(alphabet))
    int_to_char = dict((i, c) for i, c in enumerate(alphabet))

    # integer encode input data
    integer_encoded = [char_to_int[char] for char in alphabet]

    # one hot encode
    onehot_encoded = list()
    for value in integer_encoded:
        letter = [0 for _ in range(len(alphabet))]
        letter[value] = 1
        onehot_encoded.append(letter)

    ngram_vectorize = []

    # encode n-grams
    for word in dataset:
        vec = encode_word(word, alphabet, char_to_int, onehot_encoded)
        ngram_vectorize.append(vec)

    n_components = 7

    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(ngram_vectorize)

    num_clusters = 56
    vector_array = np.asarray(principal_components)
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(vector_array.T, num_clusters, 2, error=0.005, maxiter=10000,
                                                     init=None)

    word2pc = {}
    for i, w in enumerate(dataset):
        word2pc[w] = vector_array[i]

    word2predict = {}
    for i, w in enumerate(dataset):
        word2predict[w] = u.T[i]

    cluster_membership = np.argmax(u, axis=0)

    dataframes = []
    dataset_arr = np.asarray(dataset)
    for i in range(num_clusters):
        words_cl = dataset_arr[cluster_membership == i]
        i_dataframe = pd.DataFrame({'#' + str(i): words_cl})
        dataframes.append(i_dataframe)

    pd.concat(dataframes, axis=1)

    word1 = '5мм'
    word2 = '5мм'

    pcVec1 = word2pc[word1]
    pcVec2 = (word2pc['5'] + word2pc['мм']) / 2
    # pcVec2 = pcVec2 / np.linalg.norm(pcVec2)

    vecDiff = pcVec1 - pcVec2

    predict1 = predict(pcVec1, cntr)
    predict2 = predict(pcVec2, cntr)
    predictDiff = predict1 - predict2

    return dataframes, word2pc, word2predict, cntr
