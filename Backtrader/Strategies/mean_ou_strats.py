import backtrader as bt

import datetime  # For datetime objects
import numpy as np
import pandas as pd
from datetime import datetime

# Create a Strategy
class OverUnderMean(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # self.sentiment = self.datas[0].sentiment_mean
        self.size = self.data.buflen()
        self.order = None
        self.total_position = 0
        self.sum = 0
        self.count = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:

            if not self.position:
                print('(CLOSE)', end=' ')
                this_pos = abs(self.total_position)
                self.total_position = 0
            else:
                this_pos = abs(self.position.size)
                self.total_position += self.position.size
            if order.isbuy():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'BUY EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                # print(self.sentiment[0], 'Hii')
            elif order.issell():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'SELL EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                # self.log('SELL EXECUTED, %.2f' % order.executed.price)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Close all positions at the Close of the day
        if self.order:
            return

        # print(mean,len(self))
        if self.datas[0].sentiment_mean != 0:
            # this is to buy and hold only for period with sentiment data
            self.sum += self.datas[0].sentiment_mean
            self.count += 1
            mean = self.sum / self.count
            if self.datas[0].sentiment_mean < mean:
                self.order = self.buy(exectype=bt.Order.Market, coc=False)
            elif self.datas[0].sentiment_mean > mean:
                self.order = self.sell(exectype=bt.Order.Market, coc=False)

        if self.position.size:
            if len(self) == self.size or self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d') != self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d'):
                self.order = self.close(exectype=bt.Order.Close)
                # print(self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d'),self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d'))
