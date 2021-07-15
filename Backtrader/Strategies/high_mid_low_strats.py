import backtrader as bt

import datetime  # For datetime objects
import numpy as np
import pandas as pd
from datetime import datetime

# Bracket Orders BUY + Cloase each day
class HighMidLow(bt.Strategy):
    params = dict(
        stop_loss=0.92,  # price is 2% less than the entry point
        take_profit=10.04,
        orders=dict(),
        msg=''
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(sep=' ', timespec='auto'), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.sentiment = self.datas[0].sentiment_mean
        self.size = self.data.buflen()
        self.order = None
        self.stop_order = None
        self.tp_order = None
        self.total_position = 0

    def notify_order(self, order):

        # Save submitted order
        if order.status in [order.Submitted, order.Accepted]:
            self.p.orders[order.ref] = order
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:

            if not self.position:
                print('(CLOSE)', end=' ')
            else:
                self.log(self.p.msg)

            if order.isbuy():
                self.log('BUY EXECUTED, ' + str(order.size) + 'BTC AT ' + str(order.executed.price))
            elif order.issell():
                self.log('SELL EXECUTED, ' + str(order.size) + 'BTC AT ' + str(order.executed.price))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order.status == order.Canceled:
                self.log('Order Canceled')
            elif order.status == order.Margin:
                self.log('Not Enough Margin')
            elif order.status == order.Rejected:
                self.log('Order Rejected')

        self.order = None

    def next(self):
        if self.order:
            return
        # if not self.position.size:
        # this is to play only on periods with sentiment data
        if self.datas[0].sentiment_mean > 0.0:
            # High
            if self.datas[0].sentiment_mean >= 0.7:
                # Mid
                #             if self.datas[0].sentiment_mean < 0.7 and self.datas[0].sentiment_mean > 0.633:
                # Low
                #             if self.datas[0].sentiment_mean <= 0.633:

                # position size
                pos_size = self.broker.getcash() * 0.1 / self.datas[0].open[0]
                # stop loss price
                sl_price = self.datas[0].open[0] * (1 - self.p.stop_loss)
                # take profit price
                tp_price = self.datas[0].open[0] * (1 + self.p.take_profit)

                # Debug message
                self.p.msg = 'BUY CREATED AT ' + str(self.datas[0].open[0]) + ' STOPLOSS SET AT ' + str(
                    sl_price) + '$ TAKE PROFIT AT ' + str(tp_price) + '$'

                # Bracket order buy
                self.order = self.buy_bracket(exectype=bt.Order.Market,
                                              stopprice=sl_price,
                                              limitprice=tp_price,
                                              size=pos_size
                                              )

        # Close all positions at the Close of the day
        if self.position.size:
            if len(self) == self.size or self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d') != self.datas[
                0].datetime.datetime(1).strftime('%Y-%m-%d'):
                self.order = self.close(exectype=bt.Order.Close)
                # and Cancel all pending orders
                for o in self.p.orders:
                    order = self.p.orders[o]
                    if order.alive:
                        self.cancel(order)
                self.p.orders = dict()
