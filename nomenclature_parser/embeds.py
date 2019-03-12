from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

class Embedder:
    def __init__(self, dictionary, embed_dim):
        self.dictionary = dictionary

        self.reduce_to = 40

        #vectorizer = CountVectorizer(input='content', analyzer='char_wb')
        vectorizer = TfidfVectorizer(input='content', analyzer='char_wb')
        to_dense = FunctionTransformer(lambda x: x.todense(), accept_sparse=True)
        #normalizer = Normalizer()
        normalizer = StandardScaler(with_mean=False)
        # normalizer = RobustScaler(with_centering=True)
        comp_reducer = TruncatedSVD(n_components=self.reduce_to)
        transformer = TruncatedSVD(n_components=embed_dim)
        # transformer = PCA(n_components = embed_dim, whiten=True)
        #transformer = TSNE(random_state=43, n_components=embed_dim)

        self.MAX_DELTA = 20
        self.pipeline = make_pipeline(vectorizer,
                                 to_dense,
                                 normalizer,
                                 comp_reducer,
                                 transformer)
        print("Fitting embeds: {}".format(self.pipeline))

        self.embeds_list = self.pipeline.fit_transform(dictionary)

        self.word2embed = {}
        for i, w in enumerate(dictionary):
            self.word2embed[w] = self.embeds_list[i]

    def embed(self, word):
        return self.word2embed[word]

    def embeds(self, words):
        return [self.word2embed[w] for w in words]
