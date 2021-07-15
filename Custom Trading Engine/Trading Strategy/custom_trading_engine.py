import numpy as np
import math
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import style

plt.style.use('dark_background')

import bokeh
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show
from bokeh.io import curdoc


# Trading engine
class customNLP(object):

    def __init__(self, cash=None, data=None, strategy=None, leverage=False):
        self.cash = cash
        self.data = pd.DataFrame(data)
        self.data.columns = ['Open', 'Close']
        self.data.index = data.index
        self.strategy = strategy
        self.spreads = None
        self.position_asset = 0

        self.position = 0
        self.price = None
        self.mtm = cash
        self.returns = []
        self.metrics = pd.DataFrame(columns=['Position USD', 'Position BTC', 'Price USD', 'Cash USD', 'Portfolio Marked'],
                                    index=self.data.index.values)
        # print(self.metrics)

        self.stoploss = None
        self.take_profit = None

        #Used for Bokeh plotting only
        self.data_plot = []
        self.index_plot = []

        self.leverage = leverage

    def set_cash(self, cash):
        self.cash = [cash]

    def feed_data(self, data):
        self.data = data

    def import_strategy(self, strategy):
        self.strategy = strategy

    def add_spreads(self, spreads):
        self.spreads = spreads
        self.spreads.columns = ['Spread']
        self.spreads.index = spreads.index

    # appends current open position (USD amount and price), cash in bank account,
    # value of portfolio marked to current price to metrics pandas.DataFrame
    def append_statistics(self, statistics, datetime):
        for column in statistics:
            if column == 'Position USD':
                self.metrics.loc[datetime][column] = self.position
            elif column == 'Position BTC':
                self.metrics.loc[datetime][column] = self.position_asset
            elif column == 'Price USD':
                self.metrics.loc[datetime][column] = self.price
            elif column == 'Cash USD':
                self.metrics.loc[datetime][column] = self.cash
            elif column == 'Portfolio Marked':
                self.metrics.loc[datetime][column] = self.mtm
            else:
                print("Unknown Statistic named '", column, "'")

    # updates the variable that hold current open position (USD amount and price), cash in bank account
    def update_positions(self, cash, position, price):

        self.cash = cash
        self.position += position
        self.price = price

    # Calcualtes the value of portfolio as
    # cash  +  current position marked to market price
    # and appends current portfolio stats to dataset
    def marked_to_market(self, price, index):
        # if not registered position portfolio value = cash
        if self.position_asset == 0:
            self.mtm = self.cash
            return True

        # calculates position in amounts of asset
        date = index.strftime('%Y-%m-%d')

        # multiplying by current asset price
        self.mtm = self.cash + self.position_asset * price
        # append current statistics to dataset
        self.append_statistics(['Position USD', 'Position BTC', 'Price USD', 'Cash USD', 'Portfolio Marked'], index)

        # portfolio value < 0 returns false otherwise true
        if self.mtm < 0:
            if self.verbose:
                print("Position Liquated")
            return False
        else:
            return True

    # orders engine to open a long position of a USD amount at a specific price
    def buy(self, amount, price, s, verbose = None):

        if verbose == None:
            verbose = self.verbose

        # calculates remaining cash after opening long position
        cash = self.cash - amount
        # calculate the spread adjusted price
        spread_adjusted_price = price * (1 + s)

        # if we have enough we buy, update positions return True
        if cash >= 0 or self.leverage:
            # calculate the position in asset amount
            self.position_asset += amount / spread_adjusted_price
            if verbose:
                print("Opening LONG position of ", amount, " USD at ", spread_adjusted_price, " $")
            self.update_positions(cash, amount, spread_adjusted_price)
            return True
        # return False
        else:
            # calculate the position in asset amount
            self.position_asset += self.cash / spread_adjusted_price
            if verbose:
                print("Insufficient Capital - Opening LONG position of ", self.cash, " USD at ", spread_adjusted_price, " $")
            self.update_positions(0, self.cash, spread_adjusted_price)
            return True


    # orders engine to open a short position of a USD amount at a specific price
    def sell(self, amount, price, s, verbose = None):

        if verbose == None:
            verbose = self.verbose

        # calculates remaining cash after opening short position
        cash = self.cash + amount
        # calculate the spread adjusted price
        spread_adjusted_price = price * (1 - s)
        # !! amount is given in absolute prices !!

        # calculate the position in asset amount
        self.position_asset -= amount / spread_adjusted_price
        # here we can always sell
        if verbose:
            print("Opening SHORT position of ", abs(amount), " USD at ", spread_adjusted_price, " $")


        # update positions
        self.update_positions(cash, -amount, spread_adjusted_price)

        return True

    # orders engine to close current position at a specific price
    def close(self, price, s):
        # if no open position return
        if self.position == 0:
            return
        elif self.position > 0:
            if self.verbose:
                print("Closing LONG position of ", self.position, " USD at ", price, " $")
            self.sell(self.position, price, s/2., verbose = False)
        else:
            if self.verbose:
                print("Closing SHORT position of ", self.position, " USD at ", price, " $")
            self.buy(-self.position, price, s/2., verbose = False)

        # self.returns.append(self.mtm - self.cash)

        # since position is closed the cash is equal to the entire portfolio value
        cash = self.mtm
        # self.position_asset = 0
        # self.position = 0
        # self.update_positions(cash, 0, price)
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
            ### I close all previous open positions at the previous close price #
            if split and date != index.strftime('%Y-%m-%d'):
                self.close(self.data.loc[prev_index]["Close"], self.spreads[date])
                # check again if total balance has gone negative terminate
                # and update statistics (we use the previous index here)
                if not self.marked_to_market(row[0], prev_index):
                    break
                self.data_plot.append(np.nan)
                self.index_plot.append(np.nan)
            self.data_plot.append(row['Open'])
            self.index_plot.append(index)

            # save ccurrent datetime for next itteration
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
                        self.close(price,  self.spreads[date])
                        prev_index = index
                        continue
            ###############################################################
            ###############################################################

            # If total balance has gone negative terminate
            if not self.marked_to_market(row[0], index):
                break

            # apply strategy and take new optimal position
            new_position = self.strategy.apply(index, self.position, self.mtm)

            # If the new optimal position is different than the last position update positions
            if math.ceil(new_position) != math.ceil(self.position):

                if self.spreads is None:
                    s = 0
                else:
                    s = self.spreads[date]
                #print(s)

                # When updating positions I close current position and open
                # a new one since trading is assumed commission free here

                # If the new position is opposite of the current position i close position including spread
                if new_position - self.position > 0:
                    self.buy(new_position - self.position, row[0], s/2.)
                elif new_position - self.position < 0:
                    self.sell(self.position - new_position, row[0], s/2.)

                # if new_position > 0:
                #     self.close(row[0])
                #     self.buy(new_position, row[0])
                # elif new_position < 0:
                #     self.close(row[0])
                #     self.sell(-new_position, row[0])

                # check again if total balance has gone negative terminate
                # and update statistics
                if not self.marked_to_market(row['Close'], index):
                    break

                # used for split datasets
            prev_index = index

        self.close(self.data.iloc[-1],  self.spreads[date])

    # plot trading strategy on price from save statistics dataset
    def plot(self):
        fig = plt.figure(figsize=(18, 10))
        plt.plot(self.data.values, color="lightskyblue")
        x = 0
        prev = 0
        for index, row in self.metrics.iterrows():
            # print(df.loc[i,"Open"])
            position = row['Position USD']
            price = row['Price USD']

            if position in self.metrics['Position USD'].dropna().values and position != prev:

                if position > 0:
                    my_color = "green"
                    s = 100 * position / (self.metrics['Position USD'].dropna().values.max() + 1)
                elif position < 0:
                    my_color = "red"
                    s = -100 * position / (self.metrics['Position USD'].dropna().values.max() + 1)
                else:
                    my_color = "yellow"
                    s = 20
                plt.scatter(x, price, color=my_color, s=s)
            prev = position
            x += 1
        plt.show()

    def plot2(self, my_data, color='steelblue', line=2):
        df = self.metrics.dropna()
        df['sign'] = df['Position USD'].apply(np.sign)
        df['change'] = df['Position USD'].diff().fillna(1)
        long = df[df['sign'] == 1][df['change'] != 0]
        short = df[df['sign'] == -1][df['change'] != 0]
        close = df[df['sign'] == 0][df['change'] != 0]
        p2 = figure(x_axis_type="datetime", title="Trading History", plot_width=800, plot_height=600)
        # p2.grid.grid_line_alpha = 1
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = 'Price'
        # p2.ygrid.band_fill_color = "lightsteelblue"
        # p2.ygrid.band_fill_alpha = 0.1

        curdoc().theme = 'dark_minimal'
        p2.circle(long.index.values, long['Price USD'].values, size=4, legend_label='long',
                  color='mediumseagreen', alpha=1)
        p2.circle(short.index.values, short['Price USD'].values, size=4, legend_label='short',
                  color='indianred', alpha=1)
        p2.circle(close.index.values, close['Price USD'].values, size=4, legend_label='close',
                  color='yellow', alpha=1)
        # p2.line(self.data.index.values, self.data['Open'].values, legend_label='avg', color='navy')
        p2.line(my_data.index.values, my_data['Open'].values, legend_label='BTC price', color='grey', alpha=0.2)
        p2.line(self.index_plot, self.data_plot, legend_label='Trading section', color=color, alpha=0.8,
                line_width=line)
        p2.legend.location = "top_left"

        # output_file("stocks.html", title="stocks.py example")

        bokeh.plotting.show(p2)