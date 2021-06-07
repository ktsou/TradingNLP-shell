import numpy as np
import math
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import style
plt.style.use('dark_background')

class customNLP(object):

    def __init__(self, cash=None, data=None, strategy=None):
        self.cash = cash
        self.data = pd.DataFrame(data, index=data.index)
        self.strategy = strategy

        self.position = 0
        self.price = None
        self.mtm = cash
        self.returns = []
        self.metrics = pd.DataFrame(columns=['Position USD', 'Price USD', 'Cash USD', 'Portfolio Marked'],
                                    index=self.data.index)
        # print(self.metrics)

        self.stoploss = None
        self.take_profit = None

    def set_cash(self, cash):
        self.cash = [cash]

    def feed_data(self, data):
        self.data = data

    def import_strategy(self, strategy):
        self.strategy = strategy

    def append_statistics(self, statistics, datetime):
        for column in statistics:
            if column == 'Position USD':
                self.metrics.loc[datetime][column] = self.position
            elif column == 'Price USD':
                self.metrics.loc[datetime][column] = self.price
            elif column == 'Cash USD':
                self.metrics.loc[datetime][column] = self.cash
            elif column == 'Portfolio Marked':
                self.metrics.loc[datetime][column] = self.mtm
            else:
                print("Unknown Statistic named '", column, "'")

    def update_positions(self, cash, position, price):
        self.cash = cash
        self.position = position
        self.price = price

    def marked_to_market(self, price, index):

        if self.price == None:
            self.mtm = self.cash
            return True

        position_asset = self.position / self.price
        self.mtm = self.cash + position_asset * price
        self.append_statistics(['Portfolio Marked'], index)
        if self.mtm < 0:
            if self.verbose:
                print("Position Liquated")
            return False
        else:
            return True

    def buy(self, amount, price, index):

        cash = self.cash - amount
        if cash >= 0:
            if self.verbose:
                print("buying ", amount, " BTC at ", price, " $")
            self.update_positions(cash, amount, price)
            self.append_statistics(['Position USD', 'Price USD', 'Cash USD'], index)
            return True
        else:
            if self.verbose:
                print("Insufficient Capital")
            return False

    def sell(self, amount, price, index):
        if self.verbose:
            print("selling ", abs(amount), " BTC at ", price, " $")
        cash = self.cash + amount
        self.update_positions(cash, -amount, price)
        self.append_statistics(['Position USD', 'Price USD', 'Cash USD'], index)
        return True

    def close(self, price, index):
        if self.position == 0:
            return
        if self.verbose:
            print("closing ", self.position, " BTC at ", price, " $")
        # self.returns.append(self.mtm - self.cash)
        cash = self.mtm
        self.update_positions(cash, 0, price)
        self.append_statistics(['Position USD', 'Price USD', 'Cash USD'], index)
        return True

    def set_stoploss(self, sl):
        self.stoploss = sl

    def set_take_profit(self, tp):
        self.take_profit = tp

    def adverse_move(self, new_price, last_price):
        return (self.position > 0) ^ (new_price - last_price >= 0)

    def run(self, split=False, verbose=True):
        self.verbose = verbose
        date = self.data.index[0].strftime('%Y-%m-%d')
        for index, row in self.data.iterrows():
            
            ### This is application specific ##############################
            ### If the dataset is splitted and suffled ####################
            ### whenever I move to a new subset (checked by date) #########
            ### I close all previous open positions at the previous price #
            if split and date != index.strftime('%Y-%m-%d'):
                self.close(self.data.loc[prev_index]["Open"], prev_index)
                date = index.strftime('%Y-%m-%d')
            ###############################################################
            ###############################################################

            # stoploss
            # We have an open position and an active stoploss
            if self.position != 0 and self.stoploss != None:
                # there is an adverse move
                if self.adverse_move(self.data.loc[index]["Open"], self.data.loc[prev_index]["Open"]):
                    if abs(self.data.loc[index]["Open"] - self.data.loc[prev_index]["Open"]) / \
                            self.data.loc[prev_index]["Open"] >= self.stoploss:
                        if self.verbose:
                            print("Stoploss Triggered at ", self.data.loc[index]["Open"])
                        price = self.price * (1 - np.sign(self.position) * self.stoploss)
                        if not self.marked_to_market(price, index):
                            break
                        self.close(price, index)
                        prev_index = index
                        continue


            # If total balance has gone negative terminate
            if not self.marked_to_market(row[0], index):
                break


            # apply strategy
            new_position = self.strategy.apply(index, self.position, row[0], self.mtm)

            # If the new optimal position is different than the last position update positions
            if math.ceil(new_position) != math.ceil(self.position):

                # When updating positions I close current position and open
                # a new one since trading is assumed commission free here
                if new_position > 0:
                    self.close(row[0], index)
                    self.buy(new_position, row[0], index)
                elif new_position < 0:
                    self.close(row[0], index)
                    self.sell(-new_position, row[0], index)

                    # used for split datasets
            prev_index = index

        self.close(self.data.iloc[-1], index)

    def plot(self):
        fig = plt.figure(figsize=(18, 10))
        plt.plot(self.data.values)
        x = 0
        for index, row in self.metrics.iterrows():
            # print(df.loc[i,"Open"])
            position = row['Position USD']
            price = row['Price USD']
            if position in self.metrics['Position USD'].dropna().values:
                if position > 0:
                    my_color = "green"
                    s = 100 * position / self.metrics['Position USD'].dropna().values.max()
                elif position < 0:
                    my_color = "red"
                    s = -100 * position / self.metrics['Position USD'].dropna().values.max()

                else:
                    my_color = "yellow"
                    s = 20
                plt.scatter(x, price, color=my_color, s=s)
            x += 1
        plt.show()
