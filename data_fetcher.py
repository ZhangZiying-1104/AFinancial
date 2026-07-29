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
    Fetch news using akshare for A‑share numeric codes.
    For non‑numeric symbols (e.g., MSFT), generate mock news.
    """
    # 1. Try real news if symbol is numeric (A‑share)
    if symbol.isdigit():
        print(f"   📰 Fetching real news for A‑share ({symbol}) via akshare...")
        try:
            news_df = ak.stock_news_em(symbol=symbol)
            if news_df is not None and not news_df.empty:
                # Normalise column names
                if 'title' in news_df.columns and 'time' in news_df.columns:
                    df = news_df[['title', 'time']].head(max_items)
                    print(f"   ✅ Retrieved {len(df)} real news items")
                    return df
                else:
                    print("   ⚠️ Column names mismatch, trying to adapt...")
                    # You can add custom column mapping here if needed
                    return pd.DataFrame()
            else:
                print("   ⚠️ akshare returned empty news data")
        except Exception as e:
            print(f"   ⚠️ akshare news fetch failed: {e}")
            # Continue to fallback

    # 2. Fallback: generate mock news (for non‑numeric symbols or on failure)
    print(f"   📰 Using mock news data for {symbol} (demo mode)")
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

# ========== 测试代码 ==========
if __name__ == "__main__":
    # 测试：获取微软近3个月数据并保存
    msft_df = save_stock_data("MSFT", period="3mo")
    
    print("\n前5行数据预览：")
    print(msft_df.head())
