import backtrader as bt

import datetime  # For datetime objects
import numpy as np
import pandas as pd
from datetime import datetime

#BNH with OCO stoploss takeprofit
class BuyAndHoldOcO(bt.Strategy):
    params = dict(
        stop_loss=0.02,  # price is 2% less than the entry point
        take_profit=0.04
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.sentiment = self.datas[0].sentiment_mean
        self.size = self.data.buflen()
        self.order = None
        self.stop_order = None
        self.tp_order = None
        self.total_position = 0

    def set_exits(self, price, buy=True):
        i = 1 if buy else -1
        order = self.sell if buy else self.buy
        if self.p.stop_loss > 0:
            stop_price = price * (1.0 - i * self.p.stop_loss)
            self.stop_order = order(exectype=bt.Order.Stop, price=stop_price)
            print('STOPLOSS SET AT ', stop_price, '$', end=' ')
        if self.p.take_profit > 0:
            take_profit_price = price * (1.0 + i * self.p.take_profit)
            self.tp_order = order(exectype=bt.Order.Limit, price=take_profit_price)
            print('TAKE PROFIT SET AT ', take_profit_price, '$', end='')
        # canceling mechanism
        if self.p.stop_loss > 0 and self.p.take_profit > 0:
            self.stop_order.oco = self.tp_order
            self.tp_order.oco = self.stop_order
        print()

    def notify_order(self, order):
        # print(self.stop_order, '\n')
        # print(order,'\n')
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order == self.tp_order:
                print('TAKE PROFIT TRIGGERED')
            elif order == self.stop_order:
                print('STOP LOSS TRIGGERED')
            close = False
            if not self.position:
                close = True
                print('(CLOSE)', end=' ')
                this_pos = abs(self.total_position)
                self.total_position = 0
                # cancel exit orders if they exist
                self.cancel(self.tp_order) if self.tp_order else None
                self.cancel(self.stop_order) if self.stop_order else None
            else:
                this_pos = abs(self.position.size)
                self.total_position += self.position.size

            if order.isbuy():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'BUY EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                self.set_exits(order.executed.price, buy=True) if order.exectype == bt.Order.Market else None
            elif order.issell():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'SELL EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                self.set_exits(order.executed.price, buy=False) if order.exectype == bt.Order.Market else None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            # self.order = None
        # Write down: no pending order
        self.order = None

    #     def next_open(self):
    #         #If no pending order buy at the Open of the day
    #         if self.order:
    #             return
    #         if not self.position.size:
    #             #this is to buy and hold only for period with sentiment data
    #             if self.datas[0].sentiment_mean > 0.0:
    #                 self.order = self.buy(exectype=bt.Order.Market, coc=False)

    def next(self):
        if self.order:
            return
        #         if not self.position.size:
        # this is to buy and hold only for period with sentiment data
        if self.datas[0].sentiment_mean > 0.0:
            #                 if self.datas[0].sentiment_mean < 0.7 and self.datas[0].sentiment_mean > 0.633:
            self.order = self.buy(exectype=bt.Order.Market, coc=False)
        # Close all positions at the Close of the day
        if self.position.size:
            if len(self) == self.size or self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d') != self.datas[
                0].datetime.datetime(1).strftime('%Y-%m-%d'):
                self.order = self.close(exectype=bt.Order.Close)
                # print(self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d'),self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d'))


# Create a Strategy
class BuyAndHold(bt.Strategy):
    params = dict(
        stop_loss=0.02,  # price is 2% less than the entry point
    )

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

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            close = False
            if not self.position:
                close = True
                print('(CLOSE)', end=' ')
                this_pos = abs(self.total_position)
                self.total_position = 0
            else:
                this_pos = abs(self.position.size)
                self.total_position += self.position.size
            if order.isbuy():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'BUY EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                if not close:
                    stop_price = order.executed.price * (1.0 - self.p.stop_loss)
                    take_profit_price = order.executed.price * (1.0 + 3 * self.p.stop_loss)
            #                     self.order = self.sell(exectype=bt.Order.Limit, price=stop_price)
            #                     self.order = self.sell(exectype=bt.Order.Limit, price=take_profit_price)
            #                     print('STOPLOSS SET AT ', stop_price, '$ TAKE PROFIT AT ', take_profit_price,'$')
            # print(self.sentiment[0], 'Hii')
            elif order.issell():
                print(self.datas[0].datetime.datetime(-1).isoformat(), 'SELL EXECUTED, ', this_pos, 'BTC AT ',
                      order.executed.price)
                if not close:
                    stop_price = order.executed.price * (1.0 + self.p.stop_loss)
                    take_profit_price = order.executed.price * (1.0 - 3 * self.p.stop_loss)
            #                     self.order = self.buy(exectype=bt.Order.Limit, price=stop_price)
            #                     self.order = self.buy(exectype=bt.Order.Limit, price=take_profit_price)
            #                     print('STOPLOSS SET AT ', stop_price, '$ TAKE PROFIT AT ', take_profit_price,'$')
            # self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    #     def next_open(self):
    #         #If no pending order buy at the Open of the day
    #         if self.order:
    #             return
    #         if not self.position.size:
    #             #this is to buy and hold only for period with sentiment data
    #             if self.datas[0].sentiment_mean > 0.0:
    #                 self.order = self.buy(exectype=bt.Order.Market, coc=False)

    def next(self):
        if self.order:
            return
        if not self.position.size:
            # this is to buy and hold only for period with sentiment data
            if self.datas[0].sentiment_mean > 0.0:
                self.order = self.buy(exectype=bt.Order.Market, coc=False)

        # Close all positions at the Close of the day
#         if self.position.size:
#             if len(self) == self.size or self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d')!=self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d'):
#                 self.order = self.close(exectype=bt.Order.Close)
#                 #print(self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d'),self.datas[0].datetime.datetime(1).strftime('%Y-%m-%d'))
