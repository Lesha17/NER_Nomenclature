from numpy import array
from numpy import argmax
import numpy as np
import skfuzzy as fuzz
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd

text_file = open("output2.txt", "r")

dataset=text_file.read().splitlines()
dataset=list(filter(None,dataset))

# define universe of possible input values
alphabet = set('')
for l in dataset:
    alphabet=alphabet.union(set(l))
print(alphabet)
# define a mapping of chars to integers
char_to_int = dict((c, i) for i, c in enumerate(alphabet))
int_to_char = dict((i, c) for i, c in enumerate(alphabet))
# integer encode input data
integer_encoded = [char_to_int[char] for char in alphabet]
print(integer_encoded)

# one hot encode
onehot_encoded = list()
for value in integer_encoded:
	letter = [0 for _ in range(len(alphabet))]
	letter[value] = 1
	onehot_encoded.append(letter)
#print(onehot_encoded)

print(len(onehot_encoded))

import math

ngram_vectorize=[]

# encode n-grams
for word in dataset:
    vec=[0]*len(alphabet)
    for c in list(word):
        vec+=array(onehot_encoded[char_to_int[c]])
    vec_len_2 = 0
    for x in vec:
        vec_len_2 += (x * x)
    vec = vec * (1 / math.sqrt(vec_len_2))
    ngram_vectorize.append(vec)

vector_array=np.asarray(ngram_vectorize)
vector_array.shape

print(fpc)

pca = PCA(n_components=2)
principalComponents = pca.fit_transform(ngram_vectorize)

plt.scatter(principalComponents[:,0], principalComponents[:,1])
plt.show()

vector_array=np.asarray(principalComponents)
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        vector_array.T,3, 2, error=0.005, maxiter=10000, init=None)
print(fpc)

u, u0, d, jm, p, fpc = fuzz.cluster.cmeans_predict(
    vector_array.T, cntr, 2, error=0.005, maxiter=10000)

# There we identify the cluster of each word
cluster_membership = np.argmax(u, axis=0)

dataset_arr=np.asarray(dataset)
words_cl_1=dataset_arr[cluster_membership == 0]
words_cl_2=dataset_arr[cluster_membership == 1]
words_cl_3=dataset_arr[cluster_membership == 2]

df_data=np.array([words_cl_1,words_cl_2,words_cl_3])
name_dataframe = pd.DataFrame({'Name':df_data[0]})
size_dataframe=pd.DataFrame({'Size':df_data[2]})
model_dataframe=pd.DataFrame({'Model':df_data[1]})
pd.concat([name_dataframe,size_dataframe,model_dataframe], axis=1)
