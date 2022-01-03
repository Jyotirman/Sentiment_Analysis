
# from _typeshed import Self
from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import sklearn
import os
from numpy import equal
import tweepy
import csv
import re
from textblob import TextBlob
import matplotlib
# from tweepy import api
matplotlib.use('agg')


second = Blueprint("second", __name__, static_folder="static",
                   template_folder="templates")


@second.route("/sentiment_analyzer")
def sentiment_analyzer():
    return render_template("sentiment_analyzer.html")


class SentimentAnalysis:
    def __init__(self):
        self.tweets = []
        self.tweetText = []

    def DownloadData(self, keyword, tweets):

        # consumerKey = 'vcQjPvO2ba2KgIKDHQD9wKvQb' previousone
        consumerKey = 'qWab9AKRBZDG3ZGutmqXoahmr'
        # consumerSecret = 'ESIuWQmm2Xn0BmupOLAuH4GSEUsMsMgRhptm4b0wsZD8PbW5s6' previousone
        consumerSecret = '3aZmrbU8gFC7cvksehrd2f1YR7mIFFs5mTGYWs84MvmBKoB9QL'
        # BearerToken = 'AAAAAAAAAAAAAAAAAAAAABJoWQEAAAAAuml85jjkLovwKz5coPGrckLrH7s%3DJ81H889zZ6r50BL1jc9zLL9N16dB0WMoIpV6dw3o8n8azj0F9z'
        accessToken = '1465725939040468999-CCCZuAb1RJOYv6VuCUgU56gcintin7'
        accessTokenSecret = 'eeO35QcPr0TmABN4YY1MvobaijNSGi2b8YsCP0EvI4SUT'
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        tweets = int(tweets)

        self.tweets = tweepy.Cursor(
            api.search_tweets, q=keyword, lang="en").items(tweets)

        csvFile = open('result.csv', 'a')

        csvWriter = csv.writer(csvFile)

        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0

        for tweet in self.tweets:
            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))

            analysis = TextBlob(tweet.text)
            # score = SentimentIntensityAnalyzer().polarity_scores(tweet.text)
            polarity += analysis.sentiment.polarity

            if(analysis.sentiment.polarity == 0):
                neutral += 1
            elif(analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif(analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif(analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif(analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif(analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif(analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1

        csvWriter.writerow(self.tweetText)
        csvFile.close()

        positive = self.percentage(positive, tweets)
        wpositive = self.percentage(wpositive, tweets)
        spositive = self.percentage(spositive, tweets)
        negative = self.percentage(negative, tweets)
        wnegative = self.percentage(wnegative, tweets)
        snegative = self.percentage(snegative, tweets)
        neutral = self.percentage(neutral, tweets)

        polarity = polarity / tweets

        if (polarity == 0):
            htmlpolarity = "Neutral"

        # print("Neutral")
        elif (polarity > 0 and polarity <= 0.3):
            htmlpolarity = "Weakly Positive"
            # print("Weakly Positive")
        elif (polarity > 0.3 and polarity <= 0.6):
            htmlpolarity = "Positive"
        elif (polarity > 0.6 and polarity <= 1):
            htmlpolarity = "Strongly Positive"
        elif (polarity > -0.3 and polarity <= 0):
            htmlpolarity = "Weakly Negative"
        elif (polarity > -0.6 and polarity <= -0.3):
            htmlpolarity = "Negative"
        elif (polarity > -1 and polarity <= -0.6):
            htmlpolarity = "strongly Negative"

        self.plotPieChart(positive, wpositive, spositive, negative,
                          wnegative, snegative, neutral, keyword, tweets)

        print(polarity, htmlpolarity)
        return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets

    def cleanTweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    def percentage(self, part, whole):
        temp = 100 * float(part)/float(whole)
        return format(temp, '.2f')

     def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
        plt.figure()
        mylabels = ['Positive [' + str(positive) + '%]',
                    'Weakly Positive [' + str(wpositive) + '%]',
                    'Strongly Positive [' + str(spositive) + '%]',
                    'Neutral [' + str(neutral) + '%]',
                    'Negative [' + str(negative) + '%]',
                    'Weakly negative [' + str(wnegative) + '%]',
                    'Strongly negative [' + str(snegative) + '%]']
        sizes = [positive, wpositive, spositive,
                 neutral, negative, wnegative, snegative]

        colors = ['yellowgreen', 'lightgreen', 'darkgreen',
                  'gold', 'red', 'lightsalmon', 'darkred']

        myexplode = [0.2, 0, 0, 0, 0, 0, 0]

        # patches, texts = plt.pie(sizes, colors=colors,
        #                          explode=None, shadow=True, startangle=90)
        plt.pie(sizes, colors=colors, labels=mylabels,
                explode=myexplode, shadow=True, startangle=90)

        plt.legend(mylabels, title='Polarity')
        plt.axis('equal')
        plt.tight_layout()
        strFile = r"D:\python projects\sentiments\static\images\plot1.png"

        if os.path.isfile(strFile):
            os.remove(strFile)
        plt.savefig(strFile)
        plt.show()
        # return render_template('PieChart.html')


@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    sa = SentimentAnalysis()

    polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(
        keyword, tweets)
    return render_template('sentiment_analyzer.html',                
                           polarity=polarity,
                           htmlpolarity=htmlpolarity,
                           positive=positive,
                           wpositive=wpositive,
                           spositive=spositive,
                           negative=negative,
                           wnegative=wnegative,
                           snegative=snegative,
                           neutral=neutral,
                           keyword=keyword1,
                           tweets=tweet1)


@second.route('/visualize')
def visualize():
    return render_template('PieChart.html')
