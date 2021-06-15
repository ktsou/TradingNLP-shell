import numpy as np

import string
import datetime

import numpy as np
import math
import pandas as pd
from timeit import default_timer as timer
import datetime

from pandas_datareader import data
import pandas_datareader as web
import seaborn as sns

import datetime
from datetime import timezone
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('dark_background')

from scipy.optimize import minimize
from scipy import stats
from random import sample
import statsmodels.api as sm


import statsmodels
from IPython.display import display, clear_output

from pathlib import Path

BTC_PRICE_DATA_FILEPATH = '../Data/bitstampUSD_1-min_data_2012-01-01_to_2021-03-31.csv'

# simple binary_search
def binary_search(arr, low, high, x):
    # Check base case
    if high >= low:

        mid = (high + low) // 2

        # If element is present at the middle itself
        if int(arr[mid]) == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif int(arr[mid]) > x:
            return binary_search(arr, low, mid - 1, x)

        # Else the element can only be present in right subarray
        else:
            return binary_search(arr, mid + 1, high, x)

    else:
        # Element is not present in the array
        return -1

# Properly import textual data from csv into a pandas.DataFrame
def preprocess_textual(path):

    # Import all data as 1 column
    text_data = pd.read_csv(path, sep='|', names=['col1'])

    # split data into columns with ';'
    text_data = text_data.col1.str.split(';', expand=True)

    # use first row as column names, remove it from df and readjust index
    text_data.columns = list(text_data.iloc[0])
    text_data = text_data.drop(0)
    text_data.index = np.subtract(text_data.index, 1)

    # remove columns named None
    to_be_removed = [x for x in text_data.columns if x is None]
    text_data = text_data.drop(columns=to_be_removed)

    # remove rows with username None
    to_be_removed = [i for i in text_data.index if text_data.iloc[i][0] == 'None']
    text_data = text_data.drop(to_be_removed)

    return text_data

# Properly import Bitcoin price data from csv into a pandas.DataFrame
def preprocess_BTC():

    btc_data = pd.read_csv(BTC_PRICE_DATA_FILEPATH, sep='|', names=['col1'])

    # split data into columns with ','
    btc_data = btc_data.col1.str.split(',', expand=True)

    # use first row as column names, remove it from df and readjust index
    btc_data.columns = list(btc_data.iloc[0])
    btc_data = btc_data.drop(0)
    btc_data.index = np.subtract(btc_data.index, 1)

    return btc_data

# Takes input two pandas.DataFrames :
# text_data : datetime seconds accuracy (subset)
# btc_data :  unix timestamps minutes accuracy (superset)
# find the text_data datetimes in the btc_price dataset and connect the two datasets
def connect_datasets(text_data, btc_data):

    # Find start and end datetimes of textual dataset in minute accuracy
    end = pd.to_datetime(text_data.iloc[0]['date'][:-2] + '00')
    start = pd.to_datetime(text_data.iloc[-1]['date'][:-2] + '00')

    # Convert the two datetimes into Unix timestamps to match BTC dataset
    start_ts = start.replace(tzinfo=timezone.utc).timestamp()
    end_ts = end.replace(tzinfo=timezone.utc).timestamp()
    # start_ts = int(datetime.datetime.timestamp(start))

    # Search for the two Timestamps in the BTC dataset
    start_btc = binary_search(btc_data['Timestamp'], 0, len(btc_data.index) - 1, start_ts)
    end_btc = binary_search(btc_data['Timestamp'], 0, len(btc_data.index) - 1, end_ts)

    # Get the submatrix of BTC Open price data during between the two datetimes and convert it to DataFrame
    submatrix = btc_data.iloc[start_btc:end_btc + 1]['Open'].astype(float)
    submatrix_df = pd.DataFrame(submatrix)

    # Add date column to the dataframe with the utc datetime (here only Hours)
    for i in submatrix_df.index:
        submatrix_df.loc[i, 'date'] = datetime.utcfromtimestamp(int(btc_data.loc[i, 'Timestamp'])).strftime('%H')

    # Finaly get the average Open price during each hour to match the timetable dictionary
    BTC_price_per_hour = submatrix_df.groupby(['date']).Open.apply(np.mean).reset_index()
    BTC_price_per_hour.index = [text_data.iloc[0]['date'][:-8] + str(row['date']) for idx, row in
                                BTC_price_per_hour.iterrows()]

    return BTC_price_per_hour