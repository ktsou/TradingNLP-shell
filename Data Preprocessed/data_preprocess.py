import re
import string
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from collections import Counter

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

import pickle

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

stop = set(stopwords.words("english"))

def lowercase_remove_stopwords(text):
    text = [word.lower() for word in text.split() if word.lower() not in stop]
    return " ".join(text)

def counter_word(text):
    count = Counter()
    for i in text.values:
        for word in i.split():
            count[word] += 1
    return count

class NLP_preprocess(object):
    # Count unique words
    def __init__(self, df):
        self.df = df
        self.max_length = 20
        self.tokenizer = None
        self.num_words = 0

    def preprocess_data(self, field="text"):
        self.df[field] = self.df[field].map(lambda x: remove_URL(x))
        self.df[field] = self.df[field].map(lambda x: remove_html(x))
        self.df[field] = self.df[field].map(lambda x: remove_emoji(x))
        self.df[field] = self.df[field].map(lambda x: remove_punct(x))
        self.df[field] = self.df[field].map(lambda x: lowercase_remove_stopwords(x))

    def set_tokenizer(self, field="text"):
        text = self.df[field]
        counter = counter_word(text)
        self.num_words = len(counter)
        self.tokenizer = Tokenizer(num_words=self.num_words)

    def import_tokenizer(self, path = '../NLP Model Training/tokenizer_1M.pickle'):
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