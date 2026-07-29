import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

def generate_report(symbol, company_name, stock_df, sentiment_df, result_df, output_dir="reports"):
    """Generate a complete analysis report (charts + Markdown）"""
    
    # Chinese
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # -------- create trend chart --------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Price trend
    axes[0, 0].plot(stock_df['Date'], stock_df['Close'], 'b-', linewidth=1.5)
    axes[0, 0].set_title(f'{company_name} ({symbol}) trend of stock prices')
    axes[0, 0].set_xlabel('date')
    axes[0, 0].set_ylabel('closing price ($)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # turnover
    axes[0, 1].bar(stock_df['Date'], stock_df['Volume'], alpha=0.5, color='orange')
    axes[0, 1].set_title('turnover')
    axes[0, 1].set_xlabel('date')
    axes[0, 1].set_ylabel('turnover')
    axes[0, 1].grid(True, alpha=0.3)
    
    # sentiment and price
    if len(result_df) > 0 and 'sentiment' in result_df.columns:
        ax2 = axes[1, 0].twinx()
        axes[1, 0].plot(result_df['Date'], result_df['Close'], 'b-', linewidth=1.5, label='turnover')
        ax2.plot(result_df['Date'], result_df['sentiment'], 'r-', linewidth=1.5, label='sentiment score')
        axes[1, 0].set_title('Comparison of stock prices and news sentiment')
        axes[1, 0].set_xlabel('date')
        axes[1, 0].set_ylabel('turnover ($)', color='b')
        ax2.set_ylabel('sentiment socre', color='r')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Correlation heat map
    if len(result_df) > 1:
        corr_data = result_df[['return', 'sentiment']].copy()
        # if have key data, then can add
        corr_matrix = corr_data.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1, 1])
        axes[1, 1].set_title('relevant matrix')
    
    plt.tight_layout()
    
    # save graph
    fig_path = os.path.join(output_dir, 'figures', f'{symbol}_analysis.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 graph has been saved: {fig_path}")
    
    # -------- 2. create Markdown report --------
    report_lines = []
    report_lines.append(f"# {company_name} ({symbol}) Financial sentimnet analysis report")
    report_lines.append(f"\n> Time of Create: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"\n> Data Cycle: {stock_df['Date'].min()} to {stock_df['Date'].max()}")
    
    report_lines.append("\n## 📊 Key finding")
    
    # calculate key value
    if len(result_df) > 1 and 'return' in result_df.columns and 'sentiment' in result_df.columns:
        corr_val = result_df['return'].corr(result_df['sentiment'])
        report_lines.append(f"\n- **The correlation between emotions and yield rates**: {corr_val:.4f}")
        
        if corr_val > 0.3:
            report_lines.append("  - Conclusion: News sentiment is **positively** correlated with stock prices, and positive news may drive up stock prices.")
        elif corr_val < -0.3:
            report_lines.append("  - Conclusion: News sentiment is **negative** correlated with stock prices, and positive news may drive up stock prices.")
        else:
            report_lines.append("  - Conclusion: There is **no significant correlation** between news sentiment and stock prices. Stock prices may be dominated by other factors.")
    
    # price change
    price_change = (stock_df['Close'].iloc[-1] - stock_df['Close'].iloc[0]) / stock_df['Close'].iloc[0] * 100
    report_lines.append(f"\n- **The fluctuation range during the period**: {price_change:.2f}%")
    
    # average sentiment
    if 'sentiment' in result_df.columns:
        avg_sentiment = result_df['sentiment'].mean()
        report_lines.append(f"\n- **Average news sentiment**: {avg_sentiment:.3f} (Range -1 to 1)")
    
    report_lines.append("\n## 📈 graph declaration")
    report_lines.append(f"\n![graph analysis](./figures/{symbol}_analysis.png)")
    
    report_lines.append("\n## 📝 data declaration")
    report_lines.append("\n- **stock price data**: from Yahoo Finance (through yfinance)")
    report_lines.append("\n- **news**: from East Money Information Co.,ltd. (through akshare)")
    report_lines.append("\n- **sensitive analysis**: use NLTK VADER model")
    report_lines.append("\n- **disclaimer**: This report is for learning and research purposes only and does not constitute investment advice.")
    
    # write down in document
    report_path = os.path.join(output_dir, f'{symbol}_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"   📝 The report has been saved: {report_path}")
    
    return report_path
