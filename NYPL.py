
# coding: utf-8

# In[1]:


from sklearn.metrics import f1_score
import numpy as np
import pandas as pd
from nltk.corpus import wordnet
import pandas as pd
import nltk
import glove

nltk.download('wordnet')


# In[2]:


from gensim.models import word2vec
from gensim.models.word2vec import Text8Corpus
from gensim.test.utils import common_texts, get_tmpfile






# In[3]:


from gensim.models import KeyedVectors
model = KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)


# In[4]:


import logging


# In[5]:


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[6]:


path = "./Categories.csv"


# In[7]:


df = pd.read_csv(path, encoding='latin-1')


# In[8]:


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


# In[9]:


import autocorrect
from autocorrect import spell


# In[10]:


import re
for columns in df.columns:
    df[columns] = df[columns].str.lower()
    
df


# In[11]:


L=[]

for example in df.categories:
    df1 = text_cleaner(example)
    L.append(df1)
dfnew = pd.DataFrame(L, columns=['category'])
print(dfnew)
    


# In[12]:


from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
ps = PorterStemmer()


# In[13]:


L1=[]

for example in dfnew.category:
    stem = text_cleaner(example)
    L1.append(stem)
df2 = pd.DataFrame(L1, columns=['category'])
print(df2)
  


# In[14]:


from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


# In[15]:


L2=[]

for example in df2.category:
    lemm = lemmatizer.lemmatize(example)
    L2.append(lemm)
df3 = pd.DataFrame(L2, columns=['category'])
print(df3)


# In[16]:


df3["category"]= df3["category"].str.split(" ", n = 2, expand = True)
df3


# In[17]:


words = ["suv", "love", "taj", "feet"]
for word in words:
    maxexample = ""
    maxsimilar = -1
    for example in df3.category:
        
        if word in words:
            try:
                similarity1 = model.similarity(word,example)
    #           print(word, example,similarity1)
                if(maxsimilar < similarity1 and word):
                    maxsimilar = similarity1
                    maxexample = example
            except:
                pass
    print(word, maxexample, maxsimilar)
    


# In[18]:


path = "./new1.csv"


# In[19]:


df4 = pd.read_csv(path, encoding='latin-1')

df4


# In[20]:


df4 = df4.iloc[:,:-1]


# In[21]:


df4.iloc[349:354]


# In[22]:


from functools import reduce


# In[23]:


# creating embedding for each category
category_embeddings = {}
for index,row in df4.iterrows():
    list_of_words = [word for word in row if word is not np.nan]
    category = [reduce(lambda x,y: x+' '+y,list_of_words)]
    #sum of word embedding in a row
    word_embedding_per_row = 0
    for word in list_of_words:
        try: 
            word_embedding_per_row  = word_embedding_per_row + model[word]
        except:
            pass
    #print(category[0],'\t',word_embedding_per_row.shape)
    category_embeddings.update({category[0]:word_embedding_per_row})


# In[24]:


category_embeddings['Amber']


# In[25]:


words = ["Basements", "rajasthan", "taj", "feet"]
for word in words:
    maxexample = ""
    maxsimilar = -1
    for example in df4.Category1:
        
        if word in words:
            try:
                similarity1 = model.similarity(word,example)
    #           print(word, example,similarity1)
                if(maxsimilar < similarity1 and word):
                    maxsimilar = similarity1
                    maxexample = example
            except:
                pass
    print(word, maxexample, maxsimilar)


# In[26]:


from sklearn.metrics.pairwise import cosine_similarity


# In[27]:


def cos_sim(a, b):
	"""Takes 2 vectors a, b and returns the cosine similarity according 
	to the definition of the dot product
	"""
	dot_product = np.dot(a, b)
	norm_a = np.linalg.norm(a)
	norm_b = np.linalg.norm(b)
	return dot_product / (norm_a * norm_b)


# In[124]:


word = 'Ceramics'
text_input = model[word]
maxexample = ""
maxsimilar = -1
similarity_vals=[]
i=0
for example in category_embeddings.values():
    i=i+1
    if type(example)!=int:
        try:
            cos_lib = text_input.dot(example)
            similarity_vals.append(cos_lib)
        except:
            pass
    else:
        pass
        #print("word ignored")
    #           print(word, example,similarity1)


# In[125]:


word = 'Ceramics'
text_input = model[word]
maxexample = ""
maxsimilar = -1
similarity_vals=[]
i=0
for example in category_embeddings.values():
    i=i+1
    if type(example)!=int:
        try:
            cos_lib = text_input.dot(example)
            similarity_vals.append(cos_lib)
        except:
            pass
    else:
        pass
       # print("word ignored")


# In[174]:


query = 'Aviation and Aeronautics'

def Convert(string): 
    li = list(string.split(" ")) 
    return li 
text = Convert(query)
print(text)
word_embedding = 0
for word in text:
        try: 
            word_embedding  = (word_embedding + model[word])/len(text)
        except:
            pass
similarity_vals=[]
text_input = word_embedding
print(text_input)
i=0
index_list = []
for keys,example in category_embeddings.items():
    i=i+1
    if type(example)!=int:
        try:
            cos_lib = cos_sim(text_input,example)
            similarity_vals.append(cos_lib)
            index_list.append(keys)
        except:
            pass
    #           print(word, example,similarity1)


# In[170]:


# word = 'Ceramics'
# text_input = model[word]
# maxexample = ""
# maxsimilar = -1
# similarity_vals=[]
# i=0
# index_list = []
# for keys,example in category_embeddings.items():
#     i=i+1
#     if type(example)!=int:
#         try:
#             cos_lib = cos_sim(text_input,example)
#             similarity_vals.append(cos_lib)
#             index_list.append(keys)
#         except:
#             pass
#     #           print(word, example,similarity1)


# In[175]:


np.argsort(similarity_vals)[-10:]


# In[176]:


sim_value_int = [int(index) for index in np.argsort(similarity_vals)[-10:]]


# In[177]:


[index_list[i] for i in sim_value_int]

