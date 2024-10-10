# hisData

_**This FastAPI application periodically scrapes currency exchange rate data from Yahoo Finance for specific currency pairs and periods. The scraped data is stored in SQLite database and is scheduled to update regularly using CRON jobs on [https://cron-job.org/en/](https://cron-job.org/en/)**_

---

_**The scrapped data can be retrieved from the database using the provided `/api/forex` endpoint if it does not exist in the database it will first fetch the data update it in the database and then provide the client with the data. and in the subsequent requests which corresponds to the same request it will return the stored data.**_

---

**Keep in mind that this service uses render for hosting and render shuts off the server every 15 mins if no activity is found. If the server is not responding give it around 2-5 mins to start**

## Local Setup Guide.

1. **Ensure that python3 and pip3 are installed.**

```bash
    python3 --version && pip3 --version
```

2. **Clone the Repository**:

```bash
    git clone git@github.com:2k4sm/hisData.git
    cd hisData
```

3. **Create Venv and initialize it**

```bash
    python3 -m venv .venv && source .venv/bin/activate
```

4. **Install Dependencies**:

```bash
    pip3 install -r reqs.txt
```

5. **Start the uvicorn server**:

```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 80
```

**The below provided URL's all point to the deployed URL to test these locally change them to [http://localhost:80/](http://localhost:80/)**

### _swagger-ui_: [https://hisdata.2k4sm.tech/docs](https://hisdata.2k4sm.tech/docs)

## Endpoints

### 1. healthCheck - [https://hisdata.2k4sm.tech/](https://hisdata.2k4sm.tech/)

### 2. Request Historical Forex Data

#### POST `/api/forex` [https://hisdata.2k4sm.tech/api/forex](https://hisdata.2k4sm.tech/api/forex)

**Description:** Retrieves historical foreign exchange data for a specific currency pair and period. The API first checks if the data is already stored in the database, if present it returns the data present in the database otherwise, it scrapes fresh data updates the database and then returns the data.

_Curl Command:_

```bash
curl -X POST "https://hisData.2k4sm.tech/api/forex" \
-H "Content-Type: application/json" \
-d '{
    "from_currency": "USD",
    "to_currency": "EUR",
    "period": "1M"
}'
```

_Request Example:_

```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "period": "1M"
}
```

_Response Example:_

```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "period": "1M",
  "data": [
    {
      "date": "2024-09-09",
      "open_price": 1.18,
      "high_price": 1.2,
      "low_price": 1.17,
      "close_price": 1.19,
      "adj_close": 1.19,
      "volume": 3000000
    },
    ...
  ]
}
```

### 3. Endpoint to Trigger Currency Data Scraping (Used by cronjob)

#### GET `/api/scrape`

**Description:** Triggers scraping of currency data for pairs and periods (1W, 1M, 3M, 6M, 1Y) and updates db if record not present.

_Curl Command:_

```bash
curl -X GET "https://hisdata.2k4sm.tech/api/scrape"
```

_Response Example:_

```json
{
  "status": "success",
  "message": "Scraping completed successfully.",
  "updates": 50
}
```

_CRON Job Setup:_

```bash
*/15 * * * * /usr/bin/curl -X GET "https://hisdata.2k4sm.tech/api/scrape"
```

**This CRON job has been used which triggers the scraping every 15 mins to keep the server running and updating the db only if data is changed.**

# Thank You for using hisData.

## I hope you had a great time using it.
