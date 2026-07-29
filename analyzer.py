# src/analyzer.py
import pandas as pd

def merge_and_analyze(stock_df, sentiment_df):
    """
    Merge stock price data with sentiment data and compute correlations.
    
    Parameters:
        stock_df: DataFrame with stock OHLCV and a 'Date' column (may be timezone-aware)
        sentiment_df: DataFrame with 'Date' and 'sentiment' columns (or aggregated)
    
    Returns:
        merged DataFrame with combined data and correlation results.
    """
    df = stock_df.copy()
    
    # Aggregate sentiment by day if not already aggregated
    if 'Date' in sentiment_df.columns:
        daily_sentiment = sentiment_df.groupby('Date')['sentiment'].mean().reset_index()
    else:
        # Fallback for mock data without Date column
        daily_sentiment = sentiment_df.copy()
    
    # ---- FIX: remove timezone info from both Date columns ----
    # Strip timezone from stock dates (e.g., America/New_York -> naive)
    df['Date'] = df['Date'].dt.tz_localize(None)
    
    # Strip timezone from sentiment dates if present
    if 'Date' in daily_sentiment.columns and hasattr(daily_sentiment['Date'].dt, 'tz'):
        daily_sentiment['Date'] = daily_sentiment['Date'].dt.tz_localize(None)
    # ---------------------------------------------------------
    
    # Merge on Date (left join keeps all stock dates)
    merged = df.merge(daily_sentiment, on='Date', how='left')
    
    # Fill missing sentiment with 0 (neutral)
    merged['sentiment'] = merged['sentiment'].fillna(0)
    
    # Correlation between sentiment and same-day return
    if len(merged) > 1:
        corr = merged['sentiment'].corr(merged['return'])
        print(f"   Correlation (sentiment vs same-day return): {corr:.4f}")
    else:
        print("   Not enough data for correlation.")
    
    # Lagged correlation: sentiment vs next-day return
    if len(merged) > 2:
        merged['next_day_return'] = merged['return'].shift(-1)
        corr_lag = merged['sentiment'].corr(merged['next_day_return'])
        print(f"   Correlation (sentiment vs next-day return): {corr_lag:.4f}")
    
    return merged