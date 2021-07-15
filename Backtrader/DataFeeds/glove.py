import backtrader.feeds as btfeeds

class final_dataset_feed(btfeeds.GenericCSVData):
    lines = ('sentiment_mean', 'sentiment_median',)
    params = (
        ('dtformat', '%Y-%m-%d'),
        ('tmformat', '%H:%M:%S'),
        ('sentiment_mean', 1),
        ('sentiment_median', 2),
        ('datetime', 3),
        ('time', 4),
        ('open', 5),
        ('close', 6),
        ('volume', 7),
        ('high', -1),
        ('low', -1),
        ('openinterest', -1),
    )

class glove_100k_91_min_feed(btfeeds.GenericCSVData):
    lines = ('sentiment_mean',)
    params = (
        ('nullvalue', 0.0),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('sentiment_mean' , 10),
        ('datetime' , 9),
        ('time' , -1),
        ('open' , 2),
        ('close' , 5),
        ('volume' , 6),
        ('high' , 3),
        ('low' , 4),
        ('openinterest' , -1),
    )
