from custom_trading_engine import *

class Signal2(object):

    def __init__(self, data):
        self.data = data

    def get_statistics(self, datetime):
        data = []
        for index in self.data.index:
            # print(datetime.date(), int(datetime.strftime('%H')))
            if index.date() == datetime.date() and int(index.strftime('%H')) <= int(datetime.strftime('%H')):
                data.append(self.data[index])
        # print(data)
        return np.mean(data), np.std(data)

    def get_position(self, datetime):
        mean, stdv = self.get_statistics(datetime)
        # return 10000*(self.data[datetime] - self.data[datetime.date:datetime].mean() ) / self.data[:datetime].std()
        return 10000 * (self.data[datetime] - mean) / stdv


class Signal(object):

    def __init__(self, data):
        self.data = data

    def get_statistics(self, datetime):
        data = []
        for index in self.data.index:
            # print(datetime.date(), int(datetime.strftime('%H')))
            if index.date() == datetime.date() and int(index.strftime('%H')) <= int(datetime.strftime('%H')):
                data.append(self.data[index])
        # print(data)
        return np.mean(data), np.std(data)

    def get_position(self, datetime):
        mean, stdv = self.get_statistics(datetime)
        r = 10
        # return 10000*(self.data[datetime] - self.data[datetime.date:datetime].mean() ) / self.data[:datetime].std()
        #         if self.data[datetime] > 0.7 or self.data[datetime] < 0.3:
        #             r = -10
        return (self.data[datetime] - 0.5)


class RandomSignal(object):

    def get_position(self, datetime):
        return np.random.normal(0, 20000)