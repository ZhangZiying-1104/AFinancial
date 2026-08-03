# src/data_fetcher.py
import yfinance as yf
import pandas as pd
import os
import akshare as ak
import random
from datetime import datetime, timedelta

def fetch_stock_data(symbol, period="1y"):
    """get stock historica data"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    return hist

def get_stock_info(symbol):
    """get stock basic info"""
    ticker = yf.Ticker(symbol)
    return ticker.info

def save_stock_data(symbol, period="3mo", raw_dir="data/raw"):
    """
    get and save in CSV
    
    data:
        symbol: stock symbol
        period: period
        raw_dir: save oringinal data
    """
    # 1. get data
    df = fetch_stock_data(symbol, period)
    
    # 2. Reset the index to make the dates a single column
    df.reset_index(inplace=True)
    
    # 3. Make sure the directory exists
    os.makedirs(raw_dir, exist_ok=True)
    
    # 4. save as CSV
    filename = f"{raw_dir}/{symbol}_raw.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ data have been saved: {filename}")
    print(f"   data shape: {df.shape}")
    print(f"   period: {df['Date'].min()} 至 {df['Date'].max()}")
    
    # 5. print info
    info = get_stock_info(symbol)
    company_name = info.get('longName', symbol)
    print(f"   Company Name: {company_name}")
    
    return df

def fetch_news_akshare(symbol, max_items=50):
    """
    Unified news fetcher with multiple sources and graceful fallback.
    """
    # 1. A-stock
    if symbol.isdigit():
        print(f"   📰 Fetching A-share news for {symbol} via akshare...")
        try:
            import akshare as ak
            news_df = ak.stock_news_em(symbol=symbol)
            if news_df is not None and not news_df.empty:
                if 'title' in news_df.columns and 'time' in news_df.columns:
                    df = news_df[['title', 'time']].head(max_items)
                    print(f"   ✅ Retrieved {len(df)} real A-share news items")
                    return df
        except Exception as e:
            print(f"   ⚠️ akshare A-share news failed: {e}")

    # 2. try CNBC news
    if not symbol.isdigit():
        print(f"   📰 Attempting CNBC news for {symbol}...")
        try:
            cnbc_df = fetch_cnbc_news(category='latest', max_items=max_items)
            if cnbc_df is not None and not cnbc_df.empty:
                print(f"   ✅ Retrieved {len(cnbc_df)} CNBC news items")
                return cnbc_df
        except Exception as e:
            print(f"   ⚠️ CNBC news failed: {e}")

    # 3. if fail then back
    print(f"   📰 Using mock news for {symbol} (demo mode)")
    return _generate_mock_news(symbol, max_items)


def _generate_mock_news(symbol, max_items=50):
    """Generate mock news data (internal helper)."""
    templates = [
        f"{symbol} beats earnings estimates",
        f"{symbol} stock surges on strong outlook",
        f"{symbol} downgraded by analysts",
        f"{symbol} announces new product launch",
        f"{symbol} signs strategic partnership",
        f"{symbol} quarterly profit drops, shares fall",
        f"{symbol} announces share buyback",
        f"{symbol} gets major shareholder increase",
        f"{symbol} faces intensified competition",
        f"{symbol} achieves technological breakthrough"
    ]
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(max_items)]
    random.shuffle(dates)

    data = []
    for i, d in enumerate(dates):
        title = random.choice(templates) + f" (news {i+1})"
        data.append({'title': title, 'time': d.strftime('%Y-%m-%d %H:%M:%S')})

    df = pd.DataFrame(data)
    df = df.sort_values('time', ascending=False).reset_index(drop=True)
    return df

def fetch_cnbc_news(category='latest', max_items=20):
    """
    use ycnbc get CNBC news

    """
    try:
        import ycnbc
        news = ycnbc.News()
        
        # different method
        if category == 'trending':
            news_data = news.trending()
        elif category == 'latest':
            news_data = news.latest()
        elif category == 'finance':
            news_data = news.finance()
        elif category == 'technology':
            news_data = news.technology()
        elif category == 'economy':
            news_data = news.economy()
        else:
            news_data = news.latest()  # default latest
        
        # If the returned value is a list, convert it to a DataFrame
        if isinstance(news_data, list) and len(news_data) > 0:
            df = pd.DataFrame(news_data)
            # Standardized column names (The fields returned by ycnbc may include 'title', 'pubDate', 'link', etc.)
            # The actual field names may vary. Here, compatibility measures will be taken
            if 'title' in df.columns and 'pubDate' in df.columns:
                df = df.rename(columns={'pubDate': 'time'})
            elif 'title' in df.columns and 'date' in df.columns:
                df = df.rename(columns={'date': 'time'})
            # ensure have 'time' raw
            if 'time' not in df.columns:
                # If the time cannot be found, use the current time as a placeholder
                df['time'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            # limit number
            df = df.head(max_items)
            print(f"   ✅ successfully Get {len(df)} CNBC News (category: {category})")
            return df[['title', 'time']]  # just keep key 
        else:
            print(f"   ⚠️ No CNBC News ")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"   ⚠️ Fail: Get CNBC News: {e}")
        return pd.DataFrame()

# ========== Testing ==========
if __name__ == "__main__":
    
    msft_df = save_stock_data("MSFT", period="3mo")
    
    print("\n head：")
    print(msft_df.head())
