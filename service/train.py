import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import pandas as pd
import nltk
import os
import collections
import heapq
import functools

@functools.total_ordering
class Element:
    def __init__(self, similarity, word):
        self.similarity = similarity
        self.word = word

    def __lt__(self, other):
        return self.similarity < other.similarity

    def __eq__(self, other):
        return np.logical_and(self.similarity == other.similarity, self.word == other.word)

class SimilarityModel:
    def load_model():
        from gensim.models import KeyedVectors
        if "train.model" in os.listdir("/vagrant/service/train/"):
            model = KeyedVectors.load("/vagrant/service/train/train.model", mmap='r')
        else:
            model = KeyedVectors.load_word2vec_format('/vagrant/service/train/GoogleNews-vectors-negative300.bin', binary=True, limit=300000)
            model.save("/vagrant/service/train/train.model")
        return model

    def cos_sim(a, b):
    	"""
        Takes 2 vectors a, b and returns the cosine similarity according
    	to the definition of the dot product
    	"""
    	dot_product = np.dot(a, b)
    	norm_a = np.linalg.norm(a)
    	norm_b = np.linalg.norm(b)
    	return dot_product / (norm_a * norm_b)

    def convert(string):
        li = list(string.split(" "))
        return li

    def category_embeddings(df, model):
        if "category_embeddings.dat" in os.listdir("/vagrant/service/train/"):
            category_embeddings = np.load("/vagrant/service/train/category_embeddings.dat")
        else:
            from functools import reduce
            category_embeddings = {}
            for index,row in df.iterrows():
                list_of_words = [word for word in row if word is not np.nan]
                category = [reduce(lambda x,y: x+' '+y,list_of_words)]
                word_embedding_per_row = 0
                for word in list_of_words:
                    try:
                        word_embedding_per_row  = word_embedding_per_row + model[word]
                    except:
                        pass
                category_embeddings.update({category[0]:word_embedding_per_row})
            np.save('/vagrant/service/train/category_embeddings.dat', category_embeddings)
        return category_embeddings

    def top_k_similarity(query, k):
        path = "/vagrant/service/train/Categories.csv"
        df = pd.read_csv(path, encoding='latin-1').iloc[:,:-1]
        model = SimilarityModel.load_model()
        category_embeddings = SimilarityModel.category_embeddings(df, model)
        text = SimilarityModel.convert(query)
        word_embedding = 0
        for word in text:
            try:
                word_embedding  = (word_embedding + model[word])/len(text)
            except:
                pass
        similarities = []
        heapq.heapify(similarities)
        text_input = word_embedding
        for keys,example in category_embeddings.items():
            if type(example)!=int:
                try:
                    cos_lib = SimilarityModel.cos_sim(text_input,example)
                    if cos_lib is None or math.isnan(cos_lib):
                        continue
                    else:
                        heapq.heappush(similarities, (Element(cos_lib, keys), keys))
                        if len(similarities) > k:
                            heapq.heappop(similarities)
                except:
                    pass
        res = []
        for _ in range(len(similarities)):
            res.append(heapq.heappop(similarities)[1])
        return res[::-1]

print("TESTING... SIMILARITY OF LOVE : \n")
print(SimilarityModel.top_k_similarity('love', 5))
print("\n SUCCESS ...")
