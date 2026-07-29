import pandas as pd
import numpy as np

def clean_stock_data(df):
    """clean stock data"""
    df = df.copy()
    
    
    df = df.sort_values('Date')
    
    
    df = df.ffill()
    
    
    df['return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    
    df = df.dropna(subset=['return'])
    
    return df

def clean_news_data(df):
   
    df = df.copy()
    
    # delete duplicates
    df = df.drop_duplicates(subset=['title'])
    
    # ensure datetime
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        # delet hour minute 
        df['Date'] = df['time'].dt.date
        df['Date'] = pd.to_datetime(df['Date'])
    
    return df
