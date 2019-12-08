import numpy as np
import pandas as pd
import re
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from gensim.models import word2vec
from gensim.models.word2vec import Text8Corpus
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Phrases
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
        if self.similarity == other.similarity:
            return self.word > other.word
        return self.similarity < other.similarity

    def __eq__(self, other):
        return self.similarity == other.similarity and self.word == other.word

class SimilarityModel:
    def load_model():
        sentences = word2vec.Text8Corpus('/vagrant/service/train/text8')
        if "trian.model" in os.listdir("/vagrant/service/train/"):
            model = word2vec.Word2Vec.load("/vagrant/service/train/trian.model")
        else:
            model = word2vec.Word2Vec(sentences, size=150)
            model.save("/vagrant/service/train/trian.model")
        return model

    def text_cleaner(text):
        rules = [
            {r'>\s+': u'>'},  # remove spaces after a tag opens or closes
            {r'\s+': u' '},  # replace consecutive spaces
            {r'\s*<br\s*/?>\s*': u'\n'},  # newline after a <br>
            {r'</(div)\s*>\s*': u'\n'},  # newline after </p> and </div> and <h1/>...
            {r'</(p|h\d)\s*>\s*': u'\n\n'},  # newline after </p> and </div> and <h1/>...
            {r'<head>.*<\s*(/head|body)[^>]*>': u''},  # remove <head> to </head>
            {r'<a\s+href="([^"]+)"[^>]*>.*</a>': r'\1'},  # show links instead of texts
            {r'[ \t]*<[^<]*?/?>': u''},  # remove remaining tags
            {r'^\s+': u''},  # remove spaces at the beginning
            {r'[\(\)]' : u''}
        ]
        for rule in rules:
         for (k, v) in rule.items():
            regex = re.compile(k)
            text = regex.sub(v, text)
        text = text.rstrip()
        return text.lower()

    def load_categories():
        path = "/vagrant/service/train/Categories.csv"
        L=[]
        df = pd.read_csv(path, encoding='latin-1')
        for example in df.categories:
            df1 = SimilarityModel.text_cleaner(example.lower())
            L.append(df1)
        dfnew = pd.DataFrame(L, columns=['category'])
        L2=[]
        for example in dfnew.category:
            lemm = WordNetLemmatizer().lemmatize(example)
            L2.append(lemm)
        df3 = pd.DataFrame(L2, columns=['category'])
        df3["category"] = df3["category"].str.split(" ", n = 2, expand = True)
        return df3.category.unique()

    def top_k_similarity(word, k):
        model = SimilarityModel.load_model()
        categories = SimilarityModel.load_categories()
        similarities = []
        heapq.heapify(similarities)
        for example in categories:
            try:
                similarity1 = model.similarity(word,example)
                heapq.heappush(similarities, (Element(similarity1, example), example))
                if len(similarities) > k:
                    heapq.heappop(similarities)
            except:
                pass
        res = []
        if len(similarities) == k:
            for _ in range(k):
                res.append(heapq.heappop(similarities)[1])
        return res[::-1]

print(SimilarityModel.top_k_similarity('love', 5))
