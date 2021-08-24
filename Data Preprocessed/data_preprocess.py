import re
import string
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from collections import Counter

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

import pickle

#default filepaths
EMBEDDINGS_FILEPATH = "../glove.twitter.27B.100d.txt"

#DEFAULT_IMPORT_TOKENIZER_FILEPATH = '../NLP Model Training/tokenizer_100K.pickle'
DEFAULT_IMPORT_TOKENIZER_FILEPATH = '../NLP Model Training/tokenizer_1M.pickle'

##################################################################################
#
# Text preprocessing functions
#

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

##################################################################################

##################################################################################
#
# Text spam filtering functions
#

# Generate n-grams of given text
def generate_ngrams(text, n_gram=1, stop=True):

    #remove stopwords option
    stop = set(stopwords.words("english")) if stop else {}

    #always lower case for less computations when searching
    token = [
        token for token in text.lower().split(" ") if token != "" if token not in stop
    ]
    z = zip(*[token[i:] for i in range(n_gram)])
    ngrams = [" ".join(ngram) for ngram in z]

    return ngrams

# Looks of spam 1-gramms in given text and returns the intersection of the two sets
def spam_filtering_1g(text, spam = None):
    if spam == None:
        spam_words = set(['free', 'offer', 'discount', 'sale', 'news'])
    return set(generate_ngrams(text, n_gram=1, stop=True)).intersection(spam_words)

# Looks of spam 2-gramms in given text and returns the intersection of the two sets
def spam_filtering_2g(text):
    spam_words = set(['for free', 'free btc', 'free bitcoin', '100 free', 'on sale', 'learn more', 'use code', 'check out'])
    return set(generate_ngrams(text, n_gram=2, stop=False)).intersection(spam_words)

##################################################################################

##################################################################################
#
# NLP preprocess class
#

class NLP_preprocess(object):

    # Initialize object from given dataframe
    def __init__(self, df, max_len = 50):
        self.df = df
        self.max_length = max_len
        self.tokenizer = None
        self.num_words = 0
        self.embedding_matrix = None
        self.banned_users = set()

    # Preprocess textual data for applying sentiment analysis
    def preprocess_data(self, field="text"):
        self.df[field] = self.df[field].map(lambda x: remove_URL(x))
        self.df[field] = self.df[field].map(lambda x: remove_html(x))
        self.df[field] = self.df[field].map(lambda x: remove_emoji(x))
        self.df[field] = self.df[field].map(lambda x: remove_punct(x))
        self.df[field] = self.df[field].map(lambda x: lowercase(x))
        self.df[field] = self.df[field].map(lambda x: remove_stopwords(x))
        #self.df[field] = self.df[field].map(lambda x: lowercase_remove_stopwords(x))
        
    # Get rid of spam
    def spam_filtering(self):

        # df['spam'] contains the set of spam n-gramms in every text
        #self.df['spam'] = self.df[field].map(lambda x: spam_filtering_1g(x))
        self.df['spam'] = self.df["text"].map(lambda x: spam_filtering_2g(x))
        
        # print("Texts containing suspicious phrases")
        # for text in self.df[self.df['spam'] != set()].text.sample(10).values:
        #     print(text)
        #
        #get rid of non empy sets i.e. spams
        spam_indexes = self.df[self.df['spam'] != set()].index
        self.df.drop(spam_indexes, inplace=True)

    # Get rid of suspicious users
    def flag_users(self, threshold = 100):

        spam_users = list(self.banned_users)

        # flag users that have send the same message multiple times
        self.df['duplicate'] = self.df.duplicated(subset=['text'], keep=False)
        spam_users += list(self.df[self.df['duplicate']]['username'])
        
        print("Duplicate messages in a day")
        for text in self.df[self.df['duplicate'] == True].text.sample(10).values:
            print(text)
        # flag users that have more than a threshold (default = 100) messages during a day
        messages_per_user = self.df.groupby(['username'], as_index=False).size()
        multiple_messages_users = list(messages_per_user[messages_per_user['size'] > threshold]['username'])
        spam_users += multiple_messages_users
        
        print("Over ", threshold, " messages from sender in a day")
        for user in np.random.choice(multiple_messages_users,5):
            for text in self.df[self.df['username'] == user].text.sample(2).values:
                print(text)
            
        self.banned_users = set(spam_users)

        #get rid of flagged users withing the dataframe
        self.df['flagged'] = self.df["username"].map(lambda x: {x}.intersection(self.banned_users))
        spam_indexes = self.df[self.df['flagged'] != set()].index
        self.df.drop(spam_indexes, inplace=True)



    # initialize text tokenizer
    def set_tokenizer(self, field="text"):

        text = self.df[field]

        #find the number of unique words
        counter = counter_word(text)
        self.num_words = len(counter)

        #using custom out-of-vocabulary token
        self.tokenizer = Tokenizer(num_words=self.num_words, oov_token = '<OOV>')

    # import saved tokenizer
    def import_tokenizer(self, path = DEFAULT_IMPORT_TOKENIZER_FILEPATH):
        with open(path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    # tokenize and pad sentences (used both for training and testing)
    def tokenize_and_pad(self, df = pd.DataFrame(), field="text", train = True):

        #if no df was provided use self.df (I wanted a static-like usage)
        if df.empty:
            df = self.df[field]
        else:
            df = df[field]

        #if df is a train set fit tokenizer on text
        if train:
            self.tokenizer.fit_on_texts(df)

        df_sequences = self.tokenizer.texts_to_sequences(df)
        df_padded = pad_sequences(
            df_sequences, maxlen=self.max_length, padding="post", truncating="post"
        )
        return df_padded

    # use word embeddings to calculate embeddings matrix for glove
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
