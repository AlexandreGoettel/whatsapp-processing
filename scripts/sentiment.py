"""Perform sentiment analysis on whatsapp chat."""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from reader import readChat
import numpy as np


def vader_sentiment(sentence):
    """Return the vader sentiment compound score for sentence."""
    _obj = SentimentIntensityAnalyzer()
    sentiment_dict = _obj.polarity_scores(sentence)
    return sentiment_dict["compound"]


def processData(name):
    data = readChat(name)
    authorlist = list(set(data["author"]))
    score = np.zeros(len(data))
    print("Running sentiment analysis..")
    for i, sentence in enumerate(data["text"]):
        score[i] = vader_sentiment(sentence)
    # score = np.random.random(size=len(data))
    data["sentiment"] = score

    # Record sentiments over time
    minMonth = min(data["timestamp"]).year, min(data["timestamp"]).month
    maxMonth = max(data["timestamp"]).year, max(data["timestamp"]).month
    nMonthsTotal = 1 + maxMonth[1] - minMonth[1] + 12*(maxMonth[0] - minMonth[0])

    i, _month = 0, minMonth
    sentimentMonthData = np.zeros((len(authorlist), int(nMonthsTotal)))
    while _month[0] < maxMonth[0] or _month[1] <= maxMonth[1]:
        # Apply time mask
        cond_1 = data["timestamp"].dt.year == _month[0]
        cond_2 = data["timestamp"].dt.month == _month[1]
        _monthData = data[(cond_1 == 1) & (cond_2 == 1)]

        # Separate authors, extract, and format
        for j, author in enumerate(authorlist):
            data_author = _monthData[_monthData["author"].str.contains(author)]
            # Filter out neutral sentiment
            cond_1 = data_author["sentiment"] > -0.05
            cond_2 = data_author["sentiment"] < 0.05
            data_notNeutral = data_author[(cond_1 == 0) ^ (cond_2 == 0)]

            # Fill month data with average sentiment
            sentimentMonthData[j, i] = np.mean(data_notNeutral["sentiment"])

        # Iterate month-wise
        i += 1
        if _month[1] == 12:
            _month = _month[0] + 1, 1
        else:
            _month = _month[0], _month[1] + 1

    np.savez("tmp.npz", dat=sentimentMonthData, author=authorlist,
             minMonth=minMonth, maxMonth=maxMonth)
    # plt.imshow(sentimentMonthData, vmin=-1, vmax=1, cmap="RdYlGn")
    # plt.yticks(np.arange(len(authorlist)), authorlist, rotation=0)
    # plt.show()


def main(name):
    # processData(name)
    data = np.load("tmp.npz")
    sentimentMonthData, authorlist = data["dat"], data["author"]
    minM = mdates.date2num(datetime(year=data["minMonth"][0],
                                    month=data["minMonth"][1], day=1))
    maxM = mdates.date2num(datetime(year=data["maxMonth"][0],
                                    month=data["maxMonth"][1], day=1))

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.imshow(sentimentMonthData, cmap="RdYlGn", vmin=-1, vmax=1,
              extent=[minM, maxM, 0, len(authorlist)])
    ax.xaxis_date()
    plt.yticks(np.arange(len(authorlist)), authorlist[::-1], rotation=0)
    plt.show()


if __name__ == '__main__':
    main("data/_chat.txt")
