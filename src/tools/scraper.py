import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from peewee import *
from src.models.HistoricalDataModel import HistoricalData


def scrape_yahoo_finance(quote, start_date, end_date):
    print(f"Scraping Yahoo Finance for {quote} from {start_date} to {end_date}")
    
    def date_to_timestamp(date_str):
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return int(time.mktime(dt.timetuple()))

    period1 = date_to_timestamp(start_date)
    period2 = date_to_timestamp(end_date)
    
    url = f"https://finance.yahoo.com/quote/{quote}/history?period1={period1}&period2={period2}"
    
    headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
    ]
    
    response = requests.get(url, headers=headers[random.randint(0, 1)])
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    table = soup.find('table', {'class': 'table yf-h2urb6 noDl'})
    if table is None:
        raise Exception("Failed to find historical data table after scraping Yahoo Finance provide correct to and from currency codes.")
    
    rows = table.find('tbody').find_all('tr')
    
    data = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6: 
            date = cols[0].text
            open_price = cols[1].text
            high_price = cols[2].text
            low_price = cols[3].text
            close_price = cols[4].text
            adj_close = cols[5].text
            volume = cols[6].text
            
            data.append({
                "Date": date,
                "Open": open_price,
                "High": high_price,
                "Low": low_price,
                "Close": close_price,
                "Adj Close": adj_close,
                "Volume": volume
            })
    
    return data


def save_to_sqlite(data, from_currency, to_currency, period,start_date, end_date, db):
    for row in data:
        HistoricalData.create(
            date=row['Date'],
            open_price=row['Open'],
            high_price=row['High'],
            low_price=row['Low'],
            close_price=row['Close'],
            adj_close=row['Adj Close'],
            volume=row['Volume'],
            from_currency=from_currency,
            to_currency=to_currency,
            start_date=start_date,
            end_date=end_date,
            period=period
        )
    db.commit()

# # for testing.
# if __name__ == "__main__":
#     quote = "EURUSD=X"
#     start_date = "2024-01-01"
#     end_date = "2024-10-01"
    
#     historical_data = scrape_yahoo_finance(quote, start_date, end_date)
    
#     save_to_sqlite(historical_data)