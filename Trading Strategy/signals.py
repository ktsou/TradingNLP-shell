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
        #mean, stdv = 0.5, 1
        return -10000 * (self.data[datetime] - mean) / stdv

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
        if self.data[datetime]  > 0.6 or self.data[datetime]  < 0.4:
            return self.data[datetime] - 0.45
        # elif self.data[datetime]  < 0.4:
        #     return (self.data[datetime] - 0.5)
        #return 10000 * (self.data[datetime] - mean) / stdv

class Signal4(object):

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
        #mean, stdv = self.get_statistics(datetime)
        # r = 10
        if self.data[datetime] > 0.88:
            return -1000
        elif  self.data[datetime] < 0.68:
            return 1000
        else:
            return 1

class Signal3(object):

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
        # r = 10
        # if self.data[datetime] > 0.7 or self.data[datetime] < 0.3:
        #     r = -10
        return -(self.data[datetime] - mean)/stdv


class SignalX(object):

    def __init__(self, data):
        self.data = data

    def get_statistics(self, datetime):
        data = []
        for index in self.data.index:

            # print(datetime.date(), int(datetime.strftime('%H')))
            if index.date() == datetime.date() and int(index.strftime('%H')) <= int(datetime.strftime('%H')):
                data.append(self.data[index])
        l = exp_dec(data)
        # print(data)
        return np.sum(l), np.std(data)

    def get_position(self, datetime):
        mean, stdv = self.get_statistics(datetime)
        # r = 10
        # if self.data[datetime] > 0.7 or self.data[datetime] < 0.3:
        #     r = -10
        print(-mean/2)
        return -mean/2

def exp_dec(data):
    l = []
    n = len(data)
    if n==0:
        return l
    for i in range(n-1,-1,-1):
        l.append(data[i]*math.exp(-i))
    return l

class Signal5(object):

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
        # r = 10
        # if self.data[datetime] > 0.7 or self.data[datetime] < 0.3:
        #     r = -10
        return -self.data[datetime]
    
    
class RandomSignal(object):

    def get_position(self, datetime):
        return np.random.normal(0, 20000)