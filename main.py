from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from src.models.requestModel import RequestDTO
from src.tools.scraper import scrape_yahoo_finance, save_to_sqlite
from src.models.HistoricalDataModel import HistoricalData
from src.models.HistoricalDataModel import db
app = FastAPI()


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

    
    quote = f"{request.from_currency}{request.to_currency}=X"
    

    scraped_data = scrape_yahoo_finance(quote, start_date, end_date)
    
    db.connect()
    
    save_to_sqlite(scraped_data,db=db)
    
    res = {}
    data = []
    for row in HistoricalData.select():
        data.append({
            "date": row.date,
            "open_price": row.open_price,
            "high_price": row.high_price,
            "low_price": row.low_price,
            "close_price": row.close_price,
            "adj_close": row.adj_close,
            "volume": row.volume
        })
    
    res["to_currency"] = request.to_currency
    res["from_currency"] = request.from_currency
    res["period"] = request.period
    res["data"] = data
        
    db.close()
    
    return res
