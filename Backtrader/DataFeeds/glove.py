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

class glove_1M_full_dates_min_feed(btfeeds.GenericCSVData):
    lines = ('sentiment_weighted_mean','sentiment_mean',)
    params = (
        ('nullvalue', -2),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('sentiment_weighted_mean', 10),
        ('sentiment_mean' , 11),
        ('datetime' , 9),
        ('time' , -1),
        ('open' , 2),
        ('close' , 5),
        ('volume' , 6),
        ('high' , 3),
        ('low' , 4),
        ('openinterest' , -1),
    )

class glove_1M_full_dates_hour_feed(btfeeds.GenericCSVData):
    lines = ( 'sentiment_mean','sentiment_weighted_mean',)
    params = (
        ('nullvalue', -2),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('sentiment_weighted_mean', 7),
        ('sentiment_mean', 6),
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('close', 2),
        ('volume', 5),
        ('high', 3),
        ('low', 4),
        ('openinterest', -1),
    )

#
# Daily<-function(df){
#     open = df %>%
#            group_by(day) %>%
#            summarise(Open = first(Open))
#     close = df %>%
#            group_by(day) %>%
#            summarise(Close = last(Close))
#     sentiment = df %>%
#            group_by(day) %>%
#            summarise(Sentiment = mean(Bitcoin))
#     cbind(open, close["Close"], sentiment["Sentiment"])
# }