# src/ai_explainer.py

import pandas as pd
import numpy as np

def explain_analysis(stock_df, result_df, company_name, news_df=None):
    """
    AI Financial Analyst
    
    structure：
    - Executive Summary
    - Observation
    - Interpretation
    - Risk Assessment
    - Educational
    - Questions
    """
    
    # ======================================================================
    # Layer 1: Observation
    # ======================================================================
    def get_observations(df, res_df, name):
        obs = []
        
        # Observation on Price Changes
        if len(df) > 0 and 'Close' in df.columns and 'return' in res_df.columns:
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            if price_change > 5:
                trend = "Strong Uptrend"
                trend_emoji = "🚀"
            elif price_change > 0:
                trend = "Mild Uptrend"
                trend_emoji = "📈"
            elif price_change > -5:
                trend = "Consolidation"
                trend_emoji = "➡️"
            else:
                trend = "Strong Downtrend"
                trend_emoji = "📉"
            
            obs.append(f"{trend_emoji} **Price**: {name} {'rose' if price_change > 0 else 'fell'} by {abs(price_change):.2f}% over the selected period.")
            obs.append(f"   → Market phase: **{trend}**")
        
        # Emotional observation
        if 'sentiment' in res_df.columns:
            avg_sent = res_df['sentiment'].mean()
            if avg_sent > 0.15:
                sent_desc = "Positive"
                sent_emoji = "😊"
            elif avg_sent < -0.15:
                sent_desc = "Negative"
                sent_emoji = "😞"
            else:
                sent_desc = "Neutral"
                sent_emoji = "😐"
            obs.append(f"{sent_emoji} **Sentiment**: Overall news sentiment was **{sent_desc}** (average score: {avg_sent:.2f})")
            
            # Range of emotional fluctuations
            sent_std = res_df['sentiment'].std()
            if sent_std > 0.3:
                obs.append(f"   → Sentiment was **volatile** (std: {sent_std:.2f}), suggesting disagreement among news sources.")
            elif sent_std > 0.15:
                obs.append(f"   → Sentiment was **moderately varied** (std: {sent_std:.2f}).")
            else:
                obs.append(f"   → Sentiment remained **stable** (std: {sent_std:.2f}).")
        
        # Correlation observation
        if 'sentiment' in res_df.columns and 'return' in res_df.columns:
            corr = res_df['sentiment'].corr(res_df['return'])
            if abs(corr) < 0.1:
                corr_desc = "very weak"
            elif abs(corr) < 0.3:
                corr_desc = "weak"
            elif abs(corr) < 0.5:
                corr_desc = "moderate"
            else:
                corr_desc = "strong"
            
            direction = "positive" if corr > 0 else "negative"
            obs.append(f"📊 **Correlation**: Sentiment vs returns is **{corr_desc}** and **{direction}** (r = {corr:.3f}).")
        
        # Trading volume observation
        if len(df) > 0 and 'Volume' in df.columns:
            avg_vol = df['Volume'].mean()
            max_vol = df['Volume'].max()
            obs.append(f"📊 **Volume**: Average daily volume was {avg_vol/1e6:.1f}M shares, with peak at {max_vol/1e6:.1f}M.")
        
        return obs
    
    # ======================================================================
    # Layer 2: Interpretation
    # ======================================================================
    def get_interpretations(df, res_df, name):
        interp = []
        
        # Understand relevance
        if 'sentiment' in res_df.columns and 'return' in res_df.columns:
            corr = res_df['sentiment'].corr(res_df['return'])
            
            if corr > 0.3:
                interp.append(f"**Positive correlation detected** (r = {corr:.3f}):")
                interp.append(f"News sentiment appears to influence {name}'s stock price. When news is positive, the stock tends to rise.")
                interp.append(f"Possible explanation: Investors react to news sentiment as a proxy for company health.")
            elif corr < -0.3:
                interp.append(f"**Negative correlation detected** (r = {corr:.3f}):")
                interp.append(f"This is a contrarian signal — the stock tends to fall when news is optimistic, and rise when news is pessimistic.")
                interp.append(f"Possible explanation: 'Buy the rumor, sell the news' behavior, or market over-reaction.")
            else:
                interp.append(f"**Weak correlation** (r = {corr:.3f}):")
                interp.append(f"News sentiment explains very little of {name}'s price movement.")
                interp.append(f"Possible explanation: The stock is driven by other factors such as:")
                interp.append(f"  • Broader market trends")
                interp.append(f"  • Company fundamentals (earnings, growth)")
                interp.append(f"  • Macroeconomic conditions")
                interp.append(f"  • Industry-specific events")
        
        # understand sentiment
        if 'sentiment' in res_df.columns:
            avg_sent = res_df['sentiment'].mean()
            if avg_sent > 0.1 and 'return' in res_df.columns:
                return_val = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
                if return_val < 0 and avg_sent > 0:
                    interp.append(f"**Interesting divergence**: Sentiment was positive ({avg_sent:.2f}), but the stock declined ({return_val:.2f}%).")
                    interp.append(f"This suggests that either:")
                    interp.append(f"  • News sentiment data does not capture all market information")
                    interp.append(f"  • Other factors overrode the positive news")
                    interp.append(f"  • The market is looking forward, not at current news")
        
        return interp
    
    # ======================================================================
    # Layer 3: Risk Assessment
    # ======================================================================
    def get_risk_assessment(df, res_df, name):
        risk = {}
        
        # trend risk
        if len(df) > 0 and 'return' in res_df.columns:
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            if price_change < -10:
                risk['trend'] = {"status": "Weak", "score": 8, "description": "Strong downward trend, high risk"}
            elif price_change < -3:
                risk['trend'] = {"status": "Slightly Weak", "score": 5, "description": "Mild downward pressure"}
            elif price_change < 3:
                risk['trend'] = {"status": "Neutral", "score": 3, "description": "Sideways movement"}
            elif price_change < 10:
                risk['trend'] = {"status": "Slightly Strong", "score": 2, "description": "Mild uptrend"}
            else:
                risk['trend'] = {"status": "Strong", "score": 1, "description": "Strong upward momentum"}
        
        # sentiment risk
        if 'sentiment' in res_df.columns:
            avg_sent = res_df['sentiment'].mean()
            if avg_sent < -0.2:
                risk['sentiment'] = {"status": "Negative", "score": 7, "description": "Consistently negative news sentiment"}
            elif avg_sent < -0.05:
                risk['sentiment'] = {"status": "Slightly Negative", "score": 4, "description": "Mildly negative sentiment"}
            elif avg_sent < 0.05:
                risk['sentiment'] = {"status": "Neutral", "score": 3, "description": "Neutral sentiment, no strong signal"}
            elif avg_sent < 0.2:
                risk['sentiment'] = {"status": "Slightly Positive", "score": 2, "description": "Mildly positive sentiment"}
            else:
                risk['sentiment'] = {"status": "Positive", "score": 1, "description": "Strongly positive news sentiment"}
        
        # wave risk
        if len(df) > 0 and 'return' in res_df.columns:
            volatility = res_df['return'].std() * np.sqrt(252)  # Annualized volatility
            if volatility > 0.5:
                risk['volatility'] = {"status": "High", "score": 8, "description": f"Very volatile ({volatility:.1%} annualized)"}
            elif volatility > 0.3:
                risk['volatility'] = {"status": "Medium-High", "score": 6, "description": f"Moderately volatile ({volatility:.1%} annualized)"}
            elif volatility > 0.15:
                risk['volatility'] = {"status": "Medium", "score": 4, "description": f"Average volatility ({volatility:.1%} annualized)"}
            else:
                risk['volatility'] = {"status": "Low", "score": 2, "description": f"Low volatility ({volatility:.1%} annualized)"}
        
        # comprehensive evaluation
        if risk:
            total_score = sum([r['score'] for r in risk.values()])
            max_score = len(risk) * 8
            risk_pct = total_score / max_score
            
            if risk_pct > 0.6:
                overall = "High Risk"
            elif risk_pct > 0.3:
                overall = "Medium Risk"
            else:
                overall = "Low Risk"
            
            risk['overall'] = {"status": overall, "score": risk_pct}
        
        return risk
    
    # ======================================================================
    # Layer 4: Educational
    # ======================================================================
    def get_educational_notes(res_df):
        notes = []
        terms_used = []
        
        if 'return' in res_df.columns:
            notes.append("**What is Log Return?**")
            notes.append("Log return measures the percentage change between two consecutive prices using natural logarithms.")
            notes.append("It is mathematically more stable than ordinary returns and is widely used in financial research.")
            notes.append("")
        
        if 'sentiment' in res_df.columns:
            notes.append("**What is Sentiment Score?**")
            notes.append("The sentiment score ranges from -1 (very negative) to +1 (very positive).")
            notes.append("  • > 0.15: Positive sentiment")
            notes.append("  • -0.15 to 0.15: Neutral sentiment")
            notes.append("  • < -0.15: Negative sentiment")
            notes.append("This score is calculated using the VADER model, which analyzes word choice and grammar.")
            notes.append("")
            terms_used.append("sentiment")
        
        if 'return' in res_df.columns and 'sentiment' in res_df.columns:
            corr = res_df['sentiment'].corr(res_df['return'])
            notes.append("**What is Correlation?**")
            notes.append("Correlation measures whether two variables move together:")
            notes.append("  • +1.0: Perfect positive relationship (move together)")
            notes.append("  • 0.0: No relationship (independent)")
            notes.append("  • -1.0: Perfect negative relationship (move opposite)")
            notes.append(f"In this report, the correlation is **{corr:.3f}**, which indicates a")
            if abs(corr) < 0.1:
                notes.append("very weak relationship between sentiment and price movements.")
            elif abs(corr) < 0.3:
                notes.append("weak relationship — sentiment has limited explanatory power.")
            else:
                notes.append("moderate to strong relationship — sentiment matters.")
            notes.append("")
            terms_used.append("correlation")
        
        if 'return' in res_df.columns:
            vol = res_df['return'].std() * np.sqrt(252)
            notes.append("**What is Volatility?**")
            notes.append(f"Volatility measures how much the stock price fluctuates. This stock has **{vol:.1%} annualized volatility**.")
            notes.append("  • < 15%: Low risk, stable stock")
            notes.append("  • 15-30%: Moderate risk")
            notes.append("  • > 30%: High risk, aggressive stock")
            notes.append("")
            terms_used.append("volatility")
        
        if not notes:
            notes.append("No complex financial terms were detected in this analysis.")
        
        return notes, terms_used
    
    # ======================================================================
    # Layer 5: Executive Summary
    # ======================================================================
    def get_executive_summary(df, res_df, name, risk):
        lines = []
        
        # Price summary
        if len(df) > 0 and 'return' in res_df.columns:
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            direction = "rose" if price_change > 0 else "declined"
            lines.append(f"{name} {direction} by {abs(price_change):.2f}% during the analysis period.")
        
        # Sentiment summary
        if 'sentiment' in res_df.columns:
            avg_sent = res_df['sentiment'].mean()
            if avg_sent > 0.15:
                lines.append(f"News sentiment remained generally positive (average {avg_sent:.2f}).")
            elif avg_sent < -0.15:
                lines.append(f"News sentiment leaned negative (average {avg_sent:.2f}).")
            else:
                lines.append(f"News sentiment stayed mostly neutral (average {avg_sent:.2f}).")
        
        # Correlation summary
        if 'sentiment' in res_df.columns and 'return' in res_df.columns:
            corr = res_df['sentiment'].corr(res_df['return'])
            if abs(corr) < 0.1:
                lines.append(f"Sentiment and price show almost no correlation (r = {corr:.3f}).")
            elif abs(corr) < 0.3:
                lines.append(f"Sentiment and price have a weak correlation (r = {corr:.3f}).")
            else:
                lines.append(f"Sentiment and price are moderately correlated (r = {corr:.3f}).")
        
        # Risk summary
        if 'overall' in risk:
            lines.append(f"Overall risk assessment: **{risk['overall']['status']}**.")
        
        # Final recommendation
        lines.append("")
        if 'overall' in risk and risk['overall']['status'] == "High Risk":
            lines.append("⚠️ **Caution advised** — consider waiting for clearer signals before making investment decisions.")
        elif 'overall' in risk and risk['overall']['status'] == "Medium Risk":
            lines.append("📊 **Balanced approach** — sentiment provides some insight, but combine with other analysis.")
        else:
            lines.append("✅ **Favorable conditions** — but always perform your own due diligence.")
        
        lines.append("")
        lines.append("_This analysis is for educational purposes only. Not financial advice._")
        
        return "\n".join(lines)
    
    # ======================================================================
    # Layer 6: Questions
    # ======================================================================
    def get_exploration_questions(df, res_df, name):
        questions = []
        
        # Price-related questions
        if len(df) > 0 and 'return' in res_df.columns:
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            if abs(price_change) > 5:
                questions.append(f"Why did {name} {'drop' if price_change < 0 else 'rise'} so significantly?")
                questions.append(f"Were there any earnings reports, product launches, or regulatory changes during this period?")
        
        # Correlation questions
        if 'sentiment' in res_df.columns and 'return' in res_df.columns:
            corr = res_df['sentiment'].corr(res_df['return'])
            if abs(corr) < 0.2:
                questions.append("If sentiment did not drive the price, what did?")
                questions.append("  • How did the broader market (S&P 500, Hang Seng) perform?")
                questions.append("  • Were there any changes in interest rates or economic policy?")
                questions.append("  • How did competitors perform during the same period?")
        
        # Sentiment questions
        if 'sentiment' in res_df.columns:
            avg_sent = res_df['sentiment'].mean()
            sent_std = res_df['sentiment'].std()
            if sent_std > 0.2:
                questions.append("Why was there disagreement among news sources?")
                questions.append("  • Are there conflicting views on the company's outlook?")
                questions.append("  • Is there a debate about the industry direction?")
        
        # ensure have questions
        if not questions:
            questions = [
                "How does this company's performance compare to its peers?",
                "What are the company's upcoming earnings dates?",
                "Are there any industry trends that could affect this stock?",
                "What is the company's current valuation relative to its history?"
            ]
        
        return questions
    
    # ======================================================================
    # The main execution function (calling all layers)
    # ======================================================================
    
    print("\n🧠 Running AI Financial Analyst...")
    
    # Carry out analysis at each level
    observations = get_observations(stock_df, result_df, company_name)
    interpretations = get_interpretations(stock_df, result_df, company_name)
    risk = get_risk_assessment(stock_df, result_df, company_name)
    educational_notes, terms = get_educational_notes(result_df)
    summary = get_executive_summary(stock_df, result_df, company_name, risk)
    questions = get_exploration_questions(stock_df, result_df, company_name)
    
    # Construct the final output structure
    insights = {
        "executive_summary": summary,
        "observations": observations,
        "interpretations": interpretations,
        "risk": risk,
        "educational": educational_notes,
        "questions": questions,
        "terms_detected": terms
    }
    
    # To maintain backward compatibility (insights, suggestions list), while returning formatted text
    insight_texts = []
    suggestion_texts = []
    
    # 1. Executive Summary
    insight_texts.append("📋 EXECUTIVE SUMMARY")
    insight_texts.append(summary)
    
    # 2. Observations
    insight_texts.append("\n🔍 OBSERVATIONS")
    for obs in observations:
        insight_texts.append(obs)
    
    # 3. Interpretations
    if interpretations:
        insight_texts.append("\n🤔 INTERPRETATION")
        for interp in interpretations:
            insight_texts.append(interp)
    
    # 4. Risk Assessment
    insight_texts.append("\n⚠️ RISK ASSESSMENT")
    for key, value in risk.items():
        if key == "overall":
            continue
        insight_texts.append(f"  • {key.capitalize()}: {value['status']} — {value['description']}")
    if "overall" in risk:
        insight_texts.append(f"  • Overall: **{risk['overall']['status']}**")
    
    # 5. Educational Notes
    insight_texts.append("\n📚 EDUCATIONAL NOTES")
    for note in educational_notes:
        insight_texts.append(note)
    
    # 6. Exploration Questions
    insight_texts.append("\n🤔 QUESTIONS WORTH EXPLORING")
    for q in questions:
        insight_texts.append(f"  • {q}")
    
    # 7. Extract suggestions from insights (generated by rules)
    for key, value in risk.items():
        if key == "overall":
            if value['status'] == "High Risk":
                suggestion_texts.append("⚠️ High risk detected. Consider waiting for clearer signals or reducing position size.")
            elif value['status'] == "Medium Risk":
                suggestion_texts.append("📊 Medium risk. Combine sentiment analysis with fundamental analysis.")
            else:
                suggestion_texts.append("✅ Low risk environment. Continue monitoring but conditions appear favorable.")
    
    if 'trend' in risk and risk['trend']['status'] == "Weak":
        suggestion_texts.append("📉 Trend is weak. Avoid aggressive buying in a downtrend.")
    
    if 'sentiment' in risk and risk['sentiment']['status'] == "Negative":
        suggestion_texts.append("😞 Negative sentiment may persist. Be cautious of further downside.")
    
    if len(suggestion_texts) < 3:
        suggestion_texts.append("💡 Review the exploration questions above for deeper research.")
        suggestion_texts.append("📚 Remember: This analysis is educational, not financial advice.")
        suggestion_texts.append("🔄 Consider updating this analysis with new data over time.")
    
    # Build the returned insight list
    return insight_texts, suggestion_texts[:5]
