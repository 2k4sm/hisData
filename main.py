from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from src.models.requestModel import RequestDTO
from src.tools.scraper import scrape_yahoo_finance, save_to_sqlite
from src.models.HistoricalDataModel import HistoricalData
from src.models.HistoricalDataModel import db
app = FastAPI()

@app.on_event("startup")
def startup():
    db.connect()
    db.create_tables([HistoricalData], safe=True)

@app.on_event("shutdown")
def shutdown():
    db.close()

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "time": datetime.now().strftime("%Y-%m-%d")
    }

@app.post("/api/forex-data")
def get_forex_data(request: RequestDTO):
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    if request.period == '1W':
        start_date = (datetime.today() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif request.period == '1M':
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif request.period == '3M':
        start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
    elif request.period == '6M':
        start_date = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')
    elif request.period == '1Y':
        start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    else:
        return {"error": "Invalid period. Supported values are '1W', '1M', '3M', '6M', and '1Y'."}
    
    existing_data = HistoricalData.select().where(
        (HistoricalData.from_currency == request.from_currency) & 
        (HistoricalData.to_currency == request.to_currency) & 
        (HistoricalData.period == request.period)
    )

    if existing_data.exists():
        print("Using existing data from SQLite.")
        data = []
        for row in existing_data:
            data.append({
                "date": row.date,
                "open_price": row.open_price,
                "high_price": row.high_price,
                "low_price": row.low_price,
                "close_price": row.close_price,
                "adj_close": row.adj_close,
                "volume": row.volume
            })
    else:
        quote = f"{request.from_currency}{request.to_currency}=X"
        
        scraped_data = scrape_yahoo_finance(quote, start_date, end_date)
        save_to_sqlite(scraped_data, request.from_currency, request.to_currency, request.period, db)

        data = []
        for row in HistoricalData.select().where(
            (HistoricalData.from_currency == request.from_currency) & 
            (HistoricalData.to_currency == request.to_currency) & 
            (HistoricalData.period == request.period)
        ):
            data.append({
                "date": row.date,
                "open_price": row.open_price,
                "high_price": row.high_price,
                "low_price": row.low_price,
                "close_price": row.close_price,
                "adj_close": row.adj_close,
                "volume": row.volume
            })
            
    return {
        "to_currency": request.to_currency,
        "from_currency": request.from_currency,
        "period": request.period,
        "data": data
    }