import pandas as pd
from datetime import datetime
from textblob import TextBlob


class SentimentAnalysis:
    news = []

    def __init__(self, news):
        self.news = news

    def run_sentiment_analysis(self):

        def get_polarity(text):
            return TextBlob(text).sentiment.polarity

        def get_sentiment(polarity):
            if polarity < 0:
                return 'Negative'
            elif polarity == 0:
                return 'Neutral'
            else:
                return 'Positive'

        df = pd.DataFrame(self.news["Data"])
        df["published_on"] = df["published_on"].apply(datetime.fromtimestamp)
        df.set_index("published_on", inplace=True)

        df["polarity"] = df["title"].apply(get_polarity)
        df['sentiment'] = df['polarity'].apply(get_sentiment)

        return df['sentiment'].tolist()
