from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from src.models.requestModel import RequestDTO
from src.tools.scraper import scrape_yahoo_finance, save_to_sqlite
from src.models.HistoricalDataModel import HistoricalData
from src.models.HistoricalDataModel import db


desc = """
# Historical Forex Data API

The Historical Forex Data API allows you to retrieve historical foreign exchange data from various currency pairs. 📈

## Health Check

You can **check the health status** of the API.

- **GET** `/` - Returns a simple health check response.

## Forex Data

You can **retrieve historical forex data** for specified currency pairs.

### Request Forex Data

- **POST** `/api/forex-data`

### Request Body

The request body must include the following fields:

- **from_currency**: The currency code from which you want to convert (e.g., "USD").
- **to_currency**: The currency code to which you want to convert (e.g., "EUR").
- **period**: The time period for which you want to retrieve data. Supported values:
  - `1W` - Last week
  - `1M` - Last month
  - `3M` - Last three months
  - `6M` - Last six months
  - `1Y` - Last year

### Example Request

```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "period": "1M"
}

"""

app = FastAPI(
    title="hisData",
    description=desc,
    summary="historical data api for different currency pairs on Yahoo Finance.",
    version="0.0.1",
    contact={
        "name": "Shrinibas Mahanta",
        "email": "shrinibasmahanta2004@gmail.com",
    },
)

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
        raise HTTPException(status_code=400,detail="Invalid period. Supported values are '1W', '1M', '3M', '6M', and '1Y'.")
    
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
        
        try:
            scraped_data = scrape_yahoo_finance(quote, start_date, end_date)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to retrieve data: {str(e)}")
        
        
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