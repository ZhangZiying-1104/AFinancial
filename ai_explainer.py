# src/ai_explainer.py

def explain_analysis(stock_df, result_df, company_name):
    """
    Generate plain‑English insights and actionable suggestions from analysis results.
    """
    insights = []
    suggestions = []

    # 1. Interpret price change
    price_change = (stock_df['Close'].iloc[-1] - stock_df['Close'].iloc[0]) / stock_df['Close'].iloc[0] * 100

    if price_change > 5:
        insights.append(f"📈 {company_name} rose sharply by {price_change:.2f}% during the period – very strong performance.")
        suggestions.append("Strong uptrend, but watch for pullback risk. Consider setting a stop‑loss.")
    elif price_change > 0:
        insights.append(f"📈 {company_name} edged up {price_change:.2f}% – steady and slightly bullish.")
        suggestions.append("Trend is positive. If sentiment remains optimistic, consider holding or buying on dips.")
    elif price_change > -5:
        insights.append(f"📉 {company_name} dipped slightly by {price_change:.2f}% – range‑bound consolidation.")
        suggestions.append("Direction is unclear. It may be wise to wait for a clearer signal before acting.")
    else:
        insights.append(f"📉 {company_name} dropped significantly by {price_change:.2f}% – weak performance.")
        suggestions.append("Downtrend in place. Avoid catching a falling knife; wait for stabilisation.")

    # 2. Interpret sentiment-return correlation (the core)
    if 'return' in result_df.columns and 'sentiment' in result_df.columns:
        corr = result_df['return'].corr(result_df['sentiment'])

        # Plain‑English translation
        if abs(corr) < 0.1:
            relation = "almost no relationship"
            explain = "Stock moves are largely independent of news sentiment – other factors (like broader market or fundamentals) dominate."
        elif corr < 0:
            relation = "a weak inverse relationship"
            explain = "Interesting! When news is overly optimistic, the stock tends to drop ('sell on good news'), and vice versa ('buy on bad news')."
        else:
            relation = "a positive association"
            explain = "Good news does tend to lift the stock, while bad news pushes it down – sentiment has a visible effect."

        insights.append(f"📊 The correlation between news sentiment and daily returns is {corr:.3f}, which indicates {relation}.")
        insights.append(f"💡 {explain}")

        if corr > 0.3:
            suggestions.append("Sentiment seems effective – consider using news sentiment as a short‑term trading signal.")
        elif corr < -0.3:
            suggestions.append("The market appears contrarian – consider buying during panic and being cautious during euphoria.")
        else:
            suggestions.append("Focus more on fundamentals rather than relying too heavily on news sentiment.")

    # 3. Average sentiment over the period
    if 'sentiment' in result_df.columns:
        avg_sent = result_df['sentiment'].mean()
        if avg_sent > 0.1:
            insights.append(f"😃 Overall news sentiment was positive (average score {avg_sent:.2f}) – market mood is optimistic.")
        elif avg_sent < -0.1:
            insights.append(f"😞 Overall news sentiment was negative (average score {avg_sent:.2f}) – confidence is lacking.")
        else:
            insights.append(f"😐 News sentiment was fairly neutral (average score {avg_sent:.2f}) – no extreme opinions.")

    # Ensure we have at least 3 suggestions
    while len(suggestions) < 3:
        suggestions.append("💡 Combine this report with technical indicators (e.g., moving averages) for a fuller picture. This is not financial advice.")

    return insights, suggestions[:5]  # Return at most 5 suggestions