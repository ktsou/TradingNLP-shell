import numpy as np
import math
import pandas as pd
from timeit import default_timer as timer
import datetime
import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('dark_background')

import string

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

from nltk.corpus import stopwords
from nltk.book import *

from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer

class NLP(object):

    def __init__(self, text):
        self.text = text
        self.topic = set()
        self.ne = set()
        self.sentences = nltk.tokenize.sent_tokenize(text)
        self.filtered_sentences = []
        self.filtered_words = []
        self.stopwords = set(stopwords.words("english"))
        self.topics = [
            ('Bitcoin', ["bitcoin", "btc"]),
            ('Ethereum', ["ethereum", "eth", "ether"]),
            ('Other', [''])
        ]

    def preprocess_slow(self, lowercase=True, rm_stopwords=True, rm_punctuation=True):
        for sentence in self.sentences:
            words = word_tokenize(sentence)
            words_processed = []
            for w in words:
                if lowercase:
                    w = w.lower()
                if rm_stopwords and w in self.stopwords:
                    continue
                if rm_punctuation and w in string.punctuation:
                    continue
                words_processed.append(w)
            self.filtered_sentences.append(words_processed)

    def topic_recognition_slow(self):
        sentences_topics = []
        for sentence in self.filtered_sentences:
            tagged = nltk.pos_tag(sentence)
            for w in tagged:
                this_topic = self.word_topic_slow(w)
                if this_topic != 'Other':
                    sentences_topics.append((sentence, this_topic))
                    self.topic.add(this_topic)

    def word_topic_slow(self, w):
        for topic in self.topics:
            for topic_word in topic[1]:
                if topic_word in w[0]:
                    return topic[0]

            # print((sentence, self.word_topic(w)))

    def preprocess(self, lowercase=True, rm_stopwords=True, rm_punctuation=True):
        words = word_tokenize(self.text)
        words_processed = []
        for w in set(words):
            if lowercase:
                w = w.lower()
            if rm_stopwords and w in self.stopwords:
                continue
            if rm_punctuation and w in string.punctuation:
                continue
            words_processed.append(w)
        self.filtered_words = self.filtered_words + words_processed

    def topic_recognition(self):
        sentences_topics = []
        for w in set(self.filtered_words):
            this_topic = self.word_topic(w)
            if this_topic != 'Other':
                self.topic.add(this_topic)
                if len(self.topic) == 2:
                    break

            # print((sentence, self.word_topic(w)))

    def topic_recognition_ner(self):
        # sentences_processed = []
        # for sentence in self.filtered_sentences:
        entity_doc = spacy_model(self.text)
        self.filtered_sentences = [[entity.text for entity in entity_doc.ents if entity.label_ == 'ORG']]
        self.topic_recognition()

    def word_topic(self, w):
        for topic in self.topics:
            for topic_word in topic[1]:
                if topic_word in w:
                    return topic[0]
