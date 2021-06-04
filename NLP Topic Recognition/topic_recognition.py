from NLP_class import *

def topic_recognition(text_data, flagged_usernames = [], display = ''):
    start = timer()
    timetable = pd.DataFrame(columns = ['Bitcoin', 'Ethereum', 'Both', 'All'])

    for index, row in text_data.iterrows():
        #loading_bar(index, text_data.index.size-1, display)
        if row['username'] in flagged_usernames:
            #sample removed texts
#             if np.random.randint(100) == 7:
#                 print(row['text'])
            continue
        text = NLP(row['text'])
        text.preprocess()
        text.topic_recognition()
        time = row['date'][:-6]
        if time not in timetable.index:
            timetable.loc[time] = [0, 0, 0, 0]
        if len(text.topic) == 2:
            timetable.loc[time]['Both'] += 1
        elif 'Bitcoin' in text.topic:
            timetable.loc[time]['Bitcoin'] += 1
        elif 'Ethereum' in text.topic:
            timetable.loc[time]['Ethereum'] += 1
        timetable.loc[time]['All'] += 1
    return timetable[::-1]