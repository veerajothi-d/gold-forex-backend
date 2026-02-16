from fastapi import FastAPI, Query
import yfinance as yf
import pandas as pd
from datetime import datetime

app = FastAPI()

@app.get("/history-range")
def get_history_range(days: int = Query(365, ge=1, le=365)):

    try:
        # Bulk fetch using period (more reliable than start/end)
        usd_inr = yf.download("USDINR=X", period=f"{days}d", progress=False)
        sar_usd = yf.download("SARUSD=X", period=f"{days}d", progress=False)
        gold_usd = yf.download("GC=F", period=f"{days}d", progress=False)

        # Combine data
        combined = pd.DataFrame()
        combined["USD_INR"] = usd_inr["Close"]
        combined["SAR_USD"] = sar_usd["Close"]
        combined["GOLD_USD"] = gold_usd["Close"]

        # Remove missing values
        combined.dropna(inplace=True)

        if combined.empty:
            return {"error": "No data available"}

        # SAR → INR
        combined["SAR_INR"] = combined["SAR_USD"] * combined["USD_INR"]

        # Gold 24K per 10g
        combined["GOLD_INR_24K_10G"] = (
            (combined["GOLD_USD"] * combined["USD_INR"]) / 31.1035
        ) * 10

        # Convert 24K → 22K (22/24 = 0.9167)
        combined["GOLD_INR_22K_10G"] = combined["GOLD_INR_24K_10G"] * (22 / 24)

        # Sort oldest → newest (important for Android)
        combined.sort_index(inplace=True)

        result = []

        for date, row in combined.iterrows():
            result.append({
                "date": date.strftime("%Y-%m-%d"),
                "sar_inr": round(row["SAR_INR"], 4),
                "gold_inr_22k_10g": round(row["GOLD_INR_22K_10G"], 2)
            })

        return result

    except Exception as e:
        return {"error": str(e)}
