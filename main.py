# app/main.py
import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

# Add the project root directory to sys.path to import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your analysis module
from src.data_fetcher import fetch_stock_data, get_stock_info, fetch_news_akshare, save_stock_data
from src.data_cleaner import clean_stock_data, clean_news_data
from src.sentiment_analyzer import analyze_sentiment
from src.analyzer import merge_and_analyze
from src.report_generator import generate_report
from src.ai_explainer import explain_analysis
from src.docx_generator import generate_docx_report

app = FastAPI(title="Financial Sentiment Analysis API", version="1.0")

# Mount the static file directory (for storing charts and CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Template Directory
templates = Jinja2Templates(directory="app/templates")

# ensure directory appear
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports/figures", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("app/static", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """On the home page, the analysis form is displayed"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_stock(
    request: Request,
    symbol: str = Form(...),
    period: str = Form("3mo")
):
    """
    Conduct a complete stock analysis and return the results.
    """
    try:
        # ---- 1. get stock data ----
        stock_df = fetch_stock_data(symbol, period)
        if stock_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"cannot find the data of stock {symbol} , please ensure the data structure of stock（A-stocks need to add.SS or. SZ）"
            )
        stock_df.reset_index(inplace=True)
        stock_df.to_csv(f"data/raw/{symbol}_stock_raw.csv", index=False)
        
        # get name of company
        info = get_stock_info(symbol)
        company_name = info.get('longName', symbol)

        # ---- 2. get news info ----
        news_df = fetch_news_akshare(symbol, max_items=50)
        if news_df is not None and not news_df.empty:
            news_df.to_csv(f"data/raw/{symbol}_news_raw.csv", index=False)
        else:
            # if no news，create visual data
            import numpy as np
            dates = stock_df['Date'].iloc[1:].copy()
            np.random.seed(42)
            mock_sentiment = pd.DataFrame({
                'Date': dates,
                'sentiment': np.random.normal(0, 0.3, len(dates))
            })
            mock_sentiment.to_csv(f"data/processed/{symbol}_mock_sentiment.csv", index=False)
            news_df = mock_sentiment

        # ---- 3. clean data of stock ----
        stock_clean = clean_stock_data(stock_df)
        stock_clean.to_csv(f"data/processed/{symbol}_stock_clean.csv", index=False)

        # ---- 4. sentiment analysis ----
        if 'sentiment' not in news_df.columns:
            news_clean = clean_news_data(news_df)
            news_with_sentiment = analyze_sentiment(news_clean)
            news_with_sentiment.to_csv(f"data/processed/{symbol}_news_sentiment.csv", index=False)
        else:
            news_with_sentiment = news_df

        # ---- 5. merge and analysis ----
        result = merge_and_analyze(stock_clean, news_with_sentiment)
        result.to_csv(f"data/processed/{symbol}_analysis_result.csv", index=False)

        # ---- 6. create Markdown report and graph ----
        generate_report(
            symbol=symbol,
            company_name=company_name,
            stock_df=stock_clean,
            sentiment_df=news_with_sentiment,
            result_df=result,
            output_dir="reports"
        )

        # ---- 7. create AI analysis ----
        insights, suggestions = explain_analysis(stock_clean, result, company_name)

        # ---- 8. create Word report（option） ----
        pdf_path = generate_docx_report(
            symbol=symbol,
            company_name=company_name,
            insights=insights,
            suggestions=suggestions,
            md_report_path=f"reports/{symbol}_report.md",
            figure_path=f"reports/figures/{symbol}_analysis.png",
            output_path=f"reports/{symbol}_final_report.docx"
        )

        # ---- 9. Copy the chart to the static directory (for direct access by the front end) ----
        figure_src = f"reports/figures/{symbol}_analysis.png"
        figure_dst = f"app/static/{symbol}_analysis.png"
        if os.path.exists(figure_src):
            shutil.copy(figure_src, figure_dst)
        else:
            figure_dst = None

        # ---- 10. The data to be returned to the front end ----
        result_data = {
            "symbol": symbol,
            "company_name": company_name,
            "period": period,
            "price_change": (stock_clean['Close'].iloc[-1] - stock_clean['Close'].iloc[0]) / stock_clean['Close'].iloc[0] * 100,
            "avg_sentiment": result['sentiment'].mean() if 'sentiment' in result.columns else None,
            "correlation": result['sentiment'].corr(result['return']) if 'sentiment' in result.columns and 'return' in result.columns else None,
            "insights": insights,
            "suggestions": suggestions,
            "chart_url": f"/static/{symbol}_analysis.png" if figure_dst else None,
            "word_report_url": f"/reports/{symbol}_final_report.docx",  # 注意：需要额外的下载路由
            "md_report": f"reports/{symbol}_report.md",
        }

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result": result_data,
                "now": datetime.now()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{filename}")
async def download_report(filename: str):
    """Download the generated report file (Word or MD)"""
    file_path = f"reports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="file does not exist")


# If you run it directly, start it with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)