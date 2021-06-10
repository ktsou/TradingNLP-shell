from custom_trading_engine import *


class BitcoinNLPStrategy2(object):

    def __init__(self, repos = 1.5):
        self.position = 0
        self.signal = None
        self.repos = repos

    def add_signal(self, signal):
        self.signal = signal

    def set_position(self, position):
        self.position = position

    def apply(self, datetime, prev_position, new_price, cash=1):
        new_position = self.signal.get_position(datetime)
        # print(cash, self.signal.get_position(datetime), new_position)
        self.position = prev_position
        if new_position * prev_position <= 0:
            self.position = new_position
        else:
            if abs(new_position) > abs(prev_position * 1.5):
                self.position = new_position
            elif abs(new_position) < abs(prev_position / 1.5):
                self.position = new_position

        return self.position


class BitcoinNLPStrategy(object):

    def __init__(self, repos = 1.5):
        self.position = 0
        self.signal = None
        self.repos = repos

    def add_signal(self, signal):
        self.signal = signal

    def set_position(self, position):
        self.position = position

    def apply(self, datetime, prev_position, new_price, cash = 1):
        new_position = self.signal.get_position(datetime) * cash
        # print(cash, self.signal.get_position(datetime), new_position)
        self.position = prev_position
        if new_position * prev_position < 0:
            self.position = new_position
        else:
            if abs(new_position) > abs(prev_position * self.repos):
                self.position = new_position
            elif abs(new_position) < abs(prev_position / self.repos):
                self.position = new_position

        return self.position



class BitcoinBNHStrategy(object):

    def __init__(self):
        self.position = 0
        self.signal = None

    def add_signal(self, signal):
        self.signal = signal

    def set_position(self, position):
        self.position = position

    def apply(self, datetime, prev_position, new_price, cash = 1):
        self.position = 10000

        return self.position


class BitcoinRandomStrategy(object):

    def __init__(self):
        self.position = 0
        self.signal = None
        self.max = 0
        self.min = np.inf

    def add_signal(self, signal):
        self.signal = signal

    def set_position(self, position):
        self.position = position

    def apply(self, datetime, prev_position, new_price, cash = 1):
        new_position = np.random.normal(0, 20000)
        if new_position < self.min:
            self.min = new_position
        if new_position > self.max:
            self.max = new_position
        self.position = new_position

        return self.position