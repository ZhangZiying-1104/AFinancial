#!/usr/bin/env python3
# main.py - 

import sys
import os
import pandas as pd
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ensure src content can be used
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import fetch_stock_data, get_stock_info, fetch_news_akshare
from src.data_cleaner import clean_stock_data, clean_news_data
from src.sentiment_analyzer import analyze_sentiment
from src.analyzer import merge_and_analyze
from src.report_generator import generate_report

def run_full_analysis(symbol="MSFT", period="3mo", save_plots=True):
    """
    Run the entire analysis process with one click
    
    data:
        symbol: stock symbol（like "MSFT", "AAPL", "0700.HK"）
        period: period（"1mo", "3mo", "1y"）
        save_plots: if saving the graph
    """
    print("=" * 60)
    print(f"🚀 stock analysis: {symbol}")
    print(f"📅 period: {period}")
    print("=" * 60)
    
    # -------- 1: get stock info --------
    print("\n📊 [1/6] Get Stock Information...")
    stock_df = fetch_stock_data(symbol, period)
    stock_df.reset_index(inplace=True)
    stock_df.to_csv(f"data/raw/{symbol}_stock_raw.csv", index=False)
    print(f"   ✅ Get {len(stock_df)} Stock Data")
    
    # get company info
    info = get_stock_info(symbol)
    company_name = info.get('longName', symbol)
    print(f"   📌 Company: {company_name}")
    
    # -------- 2: get news --------
    print("\n📰 [2/6] Get Finanlcial News...")
    try:
        news_df = fetch_news_akshare(symbol)  # use akshare
        if news_df is not None and len(news_df) > 0:
            news_df.to_csv(f"data/raw/{symbol}_news_raw.csv", index=False)
            print(f"   ✅ get {len(news_df)} news")
        else:
            print("   ⚠️ No news data was obtained. Simulated data will be used for demonstration")
            news_df = None
    except Exception as e:
        print(f"   ⚠️ error: not get news: {e}")
        news_df = None
    
    # -------- 3: data clean --------
    print("\n🧹 [3/6] Data Cleaning...")
    stock_clean = clean_stock_data(stock_df)
    stock_clean.to_csv(f"data/processed/{symbol}_stock_clean.csv", index=False)
    print(f"   ✅ data cleaning finished，contain {len(stock_clean)} records")
    
    # -------- 4: sentiment analysis --------
    print("\n💬 [4/6] News Sentiment Analysis...")
    if news_df is not None and len(news_df) > 0:
        news_clean = clean_news_data(news_df)
        news_with_sentiment = analyze_sentiment(news_clean)
        news_with_sentiment.to_csv(f"data/processed/{symbol}_news_sentiment.csv", index=False)
        print(f"   ✅ Emotion analysis completed, average emotion: {news_with_sentiment['sentiment'].mean():.3f}")
    else:
        # if no news, create vitual one
        import numpy as np
        print("   ⚠️ There is no news data. Simulated sentiment data is generated for demonstration")
        np.random.seed(42)
        dates = stock_clean['Date'].iloc[1:].copy()
        mock_sentiment = pd.DataFrame({
            'Date': dates,
            'sentiment': np.random.normal(0, 0.3, len(dates))
        })
        mock_sentiment.to_csv(f"data/processed/{symbol}_mock_sentiment.csv", index=False)
        news_with_sentiment = mock_sentiment
    
    # -------- 5: Merge and Analyze --------
    print("\n📈 [5/6] Carry out core analysis...")
    result = merge_and_analyze(stock_clean, news_with_sentiment)
    result.to_csv(f"data/processed/{symbol}_analysis_result.csv", index=False)
    print(f"   ✅ Analysis finish")
    print(f"   📊 The correlation between emotions and yield rates: {result['sentiment'].corr(result['return']):.4f}")
    
    # -------- 6: create report --------
    print("\n📝 [6/6] Create Report...")
    generate_report(
        symbol=symbol,
        company_name=company_name,
        stock_df=stock_clean,
        sentiment_df=news_with_sentiment,
        result_df=result,
        output_dir="reports"
    )
    print("   ✅ The Report has been created in reports/ directory")
    
    print("\n" + "=" * 60)
    print(f"🎉 Done! Please refer to the reports and charts in the reports/ directory")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    # modify parameter
    SYMBOL = "XXXX"      # Symbol
    PERIOD = "3mo"       # Period
    
    # ensure directory appear
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports/figures", exist_ok=True)
    
    # analysis
    run_full_analysis(SYMBOL, PERIOD)
