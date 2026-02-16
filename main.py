from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/history")
def get_history():

    # Date range: last 1 year
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    # Fetch data from Yahoo Finance
    usd_inr = yf.download("USDINR=X", start=start_date, end=end_date)
    sar_usd = yf.download("SARUSD=X", start=start_date, end=end_date)
    gold_usd = yf.download("GC=F", start=start_date, end=end_date)

    # Combine data
    combined = pd.DataFrame()
    combined["USD_INR"] = usd_inr["Close"]
    combined["SAR_USD"] = sar_usd["Close"]
    combined["GOLD_USD"] = gold_usd["Close"]

    # Remove rows with missing data
    combined.dropna(inplace=True)

    # Calculate SAR → INR
    combined["SAR_INR"] = combined["SAR_USD"] * combined["USD_INR"]

    # Calculate Gold price per 10 grams (24K equivalent)
    combined["GOLD_INR_24K_10G"] = (
        (combined["GOLD_USD"] * combined["USD_INR"]) / 31.1035
    ) * 10

    # Convert to 22K gold
    combined["GOLD_INR_22K_10G"] = combined["GOLD_INR_24K_10G"] * 0.9167

    # Prepare JSON response
    result = []

    for date, row in combined.iterrows():
        result.append({
            "date": date.strftime("%Y-%m-%d"),
            "sar_inr": round(row["SAR_INR"], 4),
            "gold_inr_22k_10g": round(row["GOLD_INR_22K_10G"], 2)
        })

    return result
