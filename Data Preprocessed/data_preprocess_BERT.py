from official.official import nlp

from official.official.nlp import bert

from official.official.nlp.bert import tokenization as tokenization
from official.official import modeling as modeling
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from IPython.core.debugger import set_trace

#%load_ext nb_black

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import time

import os

import numpy as np
import pandas as pd

import tensorflow as tf
import tensorflow_hub as hub

from keras.utils import np_utils

plt.style.use(style="dark_background")

#set default path
MODEL_PATH = '../NLP Model Training'

##################################################################################
#
# BERT preprocess class for calculating sentiment
#
class BERT_preprocess(object):

    def __init__(self):
        self.model = self.get_model()
        self.tokenizer = self.get_tokenizer()
        self.encoder = self.get_encoder()

    # takes a list of strings(text) returns the sentiment score of each one in a list
    def predict(self, text):
        inputs = self.bert_encode(string_list=list(text),
                             max_seq_length=200)
        prediction = self.model.predict(inputs)

        #prediction is of the form [[x1,y1],[x2,y2],...] the sentiment scores are the y's
        x, y = zip(*prediction)
        return list(y)

    # import the trained model
    def get_model(self):
        model_fname = 'model_BERT_trainable'
        my_wd = MODEL_PATH

        new_model = tf.keras.models.load_model(os.path.join(my_wd, model_fname))
        new_model.summary()
        return new_model

    # import tokenizer from saved model
    def get_tokenizer(self):
        model_fname = 'model_BERT_trainable'
        my_wd = MODEL_PATH
        # From the saved model model, we can build our tokenizer as it was.
        # vocab_file = reads the vocab file associated to the downloaded model.
        return bert.tokenization.FullTokenizer(
            vocab_file=os.path.join(my_wd, model_fname, 'assets/vocab.txt'),
            do_lower_case=False)

    #not used
    def get_encoder(self):
        encoder_fname = 'twitter_classes_train.npy'
        my_wd = MODEL_PATH

        encoder = LabelEncoder()
        encoder.classes_ = np.load(os.path.join(my_wd, encoder_fname), allow_pickle=True)
        return encoder

    def encode_names(self, n):
        tokens = list(self.tokenizer.tokenize(n))
        # seperation token for multiple text input
        tokens.append('[SEP]')
        return self.tokenizer.convert_tokens_to_ids(tokens)

    # Tokenizes the inputs (tweets) as input_word_ids and then adds input_mask and input_type
    def bert_encode(self, string_list, max_seq_length):
        num_examples = len(string_list)

        string_tokens = tf.ragged.constant([
            self.encode_names(n) for n in np.array(string_list)])

        # Add classification token as the irst token.
        cls = [self.tokenizer.convert_tokens_to_ids(['[CLS]'])] * string_tokens.shape[0]
        input_word_ids = tf.concat([cls, string_tokens], axis=-1)

        # The mask allows the model to cleanly differentiate between the content and
        # the padding. The mask has the same shape as the `input_word_ids`, and contains
        # a `1` anywhere the `input_word_ids` is not padding.
        input_mask = tf.ones_like(input_word_ids).to_tensor(shape=(None, max_seq_length))

        type_cls = tf.zeros_like(cls)
        type_tokens = tf.ones_like(string_tokens)
        input_type_ids = tf.concat(
            [type_cls, type_tokens], axis=-1).to_tensor(shape=(None, max_seq_length))

        # the 3 inputs for the bert Tokens, Input mask, Input type
        inputs = {
            'input_word_ids': input_word_ids.to_tensor(shape=(None, max_seq_length)),
            'input_mask': input_mask,
            'input_type_ids': input_type_ids}

        return inputs
