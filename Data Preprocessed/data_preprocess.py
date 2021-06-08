import re
import string
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from collections import Counter

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

import pickle

EMBEDDINGS_FILEPATH = "../glove.twitter.27B.100d.txt"

DEFAULT_IMPORT_TOKENIZER_FILEPATH = '../NLP Model Training/tokenizer_100K.pickle'

def remove_URL(text):
    url = re.compile(r"https?://\S+|www\.\S+")
    return url.sub(r"", text)

def remove_html(text):
    html = re.compile(r"<.*?>")
    return html.sub(r"", text)

def remove_emoji(string):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", string)

def remove_punct(text):
    table = str.maketrans("", "", string.punctuation)
    return text.translate(table)

# def remove_punct(text):
#     spam_words = ['free', 'offer', 'free!']
#     table = str.maketrans("", "", string.punctuation)
#     return text.translate(table)

stop = set(stopwords.words("english"))

def lowercase(text):
    text = [word.lower() for word in text.split()]
    return " ".join(text)

def remove_stopwords(text):
    text = [word for word in text.split() if word not in stop]
    return " ".join(text)

def lowercase_remove_stopwords(text):
    text = [word.lower() for word in text.split() if word.lower() not in stop]
    return " ".join(text)

def counter_word(text):
    count = Counter()
    for i in text.values:
        for word in i.split():
            count[word] += 1
    return count

def spam_filtering_1g(text):
    spam_words = set(['free', 'offer', 'discount', 'sale'])
    return set(generate_ngrams(text, n_gram=1, stop=True)).intersection(spam_words)

def spam_filtering_2g(text):
    spam_words = set(['for free', 'free btc', 'free bitcoin', '100 free', 'on sale', 'learn more', 'use_code'])
    return set(generate_ngrams(text, n_gram=2, stop=False)).intersection(spam_words)

def generate_ngrams(text, n_gram=1, stop=True):
    """
    Simple n-gram generator.
    """
    stop = set(stopwords.words("english")) if stop else {}

    token = [
        token for token in text.lower().split(" ") if token != "" if token not in stop
    ]
    z = zip(*[token[i:] for i in range(n_gram)])
    ngrams = [" ".join(ngram) for ngram in z]

    return ngrams

class NLP_preprocess(object):
    # Count unique words
    def __init__(self, df, max_len = 50):
        self.df = df
        self.max_length = max_len
        self.tokenizer = None
        self.num_words = 0
        self.embedding_matrix = None
        
    def preprocess_data(self, field="text"):
        self.df[field] = self.df[field].map(lambda x: remove_URL(x))
        self.df[field] = self.df[field].map(lambda x: remove_html(x))
        self.df[field] = self.df[field].map(lambda x: remove_emoji(x))
        self.df[field] = self.df[field].map(lambda x: remove_punct(x))
        self.df[field] = self.df[field].map(lambda x: lowercase(x))
        #self.df['spam'] = self.df[field].map(lambda x: spam_filtering_1g(x))
        self.df['spam'] = self.df[field].map(lambda x: spam_filtering_2g(x))
        self.df[field] = self.df[field].map(lambda x: remove_stopwords(x))
        #self.df[field] = self.df[field].map(lambda x: lowercase_remove_stopwords(x))
        

    def spam_filtering(self):
        spam_indexes = self.df[self.df['spam'] == set()].index
        self.df.drop(spam_indexes, inplace=True)

    def set_tokenizer(self, field="text"):
        text = self.df[field]
        counter = counter_word(text)
        self.num_words = len(counter)
        self.tokenizer = Tokenizer(num_words=self.num_words, oov_token = '<OOV>')

    def import_tokenizer(self, path = DEFAULT_IMPORT_TOKENIZER_FILEPATH):
        with open(path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def tokenize_and_pad(self, df = pd.DataFrame(), field="text", train = True):
        if df.empty:
            df = self.df[field]
        else:
            df = df[field]

        if train:
            self.tokenizer.fit_on_texts(df)

        df_sequences = self.tokenizer.texts_to_sequences(df)
        df_padded = pad_sequences(
            df_sequences, maxlen=self.max_length, padding="post", truncating="post"
        )
        return df_padded
    
    def set_embedding_matrix(self):
        embedding_dict = {}
        with open(EMBEDDINGS_FILEPATH, "r", encoding="utf8") as f:
            for line in f:
                values = line.split()
                word = values[0]
                vectors = np.asarray(values[1:], "float32")
                embedding_dict[word] = vectors
        f.close()
        word_index = self.tokenizer.word_index
        # + 2 beacause of oov
        self.num_words = len(word_index) + 2
        self.embedding_matrix = np.zeros((self.num_words, 100))
        for word, i in word_index.items():
            if i < self.num_words:
                emb_vec = embedding_dict.get(word)
                if emb_vec is not None:
                    self.embedding_matrix[i] = emb_vec
