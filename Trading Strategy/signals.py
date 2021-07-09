from custom_trading_engine import *

class Signal_mean():

    def __init__(self, data, pos = 1):
        self.data = data
        self.pos = pos

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
        return self.pos * (self.data[datetime] - mean) / stdv

class Signal_mean_window():

    def __init__(self, data, pos = 1, window_size = 50):
        self.data = data
        self.pos = pos
        self.window_size = window_size

    def get_statistics(self, datetime):
        end = self.data.index.get_loc(datetime)
        if end >= self.window_size:
            start = end - self.window_size
        else:
            start = 0

        data = []
        for idx in self.data[start:end].index:
            # print(datetime.date(), int(datetime.strftime('%H')))
            data.append(self.data[idx])

        # print(data)
        if len(data) < 2:
            std = 1
            if len(data) < 1:
                mean = 0
            else:
                mean = np.mean(data)
        else:
            mean = np.mean(data)
            std = np.std(data)
        #print(data, mean, std)
        return mean, std

    def get_position(self, datetime):
        mean, stdv = self.get_statistics(datetime)
        return self.pos * (self.data[datetime] - mean) / stdv

class Signal_standard(object):

    def __init__(self, data, pos = 0.1):
        self.data = data
        self.pos = pos

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
        mean = 0.5
        if self.data[datetime] > mean:
            return self.pos
        elif self.data[datetime] < mean:
            return -self.pos
        else:
            return 0

# Not currently used
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