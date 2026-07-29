import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


# firstly download VADER 
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def analyze_sentiment(news_df, text_column='title'):
    """Analysis"""
    df = news_df.copy()
    sia = SentimentIntensityAnalyzer()
    
    def get_sentiment(text):
        if pd.isna(text) or text == '':
            return 0.0
        return sia.polarity_scores(str(text))['compound']
    
    df['sentiment'] = df[text_column].apply(get_sentiment)
    
    return df

def aggregate_daily_sentiment(sentiment_df):
    """clustering"""
    if 'Date' not in sentiment_df.columns:
        raise ValueError("DataFrame need include 'Date' row")
    
    daily_sentiment = sentiment_df.groupby('Date')['sentiment'].mean().reset_index()
    daily_sentiment.columns = ['Date', 'sentiment']
    return daily_sentiment
