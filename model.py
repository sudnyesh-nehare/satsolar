import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import requests
import io

def fetch_and_train(latitude, longitude):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
        f"parameters=ALLSKY_SFC_SW_DWN,T2M&"
        f"community=RE&"
        f"longitude={longitude}&latitude={latitude}&"
        f"start=20230101&end=20251231&"
        f"format=CSV"
    )

    response = requests.get(url)
    raw = response.text

    for skip in range(8, 18):
        try:
            df = pd.read_csv(io.StringIO(raw), skiprows=skip)
            if 'ALLSKY_SFC_SW_DWN' in df.columns and any('YEAR' in c.upper() for c in df.columns):
                break
        except:
            pass

    cols_lower = {c.lower(): c for c in df.columns}
    year_col  = next((v for k,v in cols_lower.items() if 'year'  in k), None)
    month_col = next((v for k,v in cols_lower.items() if 'mo' in k), None)
    day_col   = next((v for k,v in cols_lower.items() if 'dy' in k), None)
    hour_col  = next((v for k,v in cols_lower.items() if 'hr' in k), None)

    df['datetime'] = pd.to_datetime(
        df[year_col].astype(str) + '-' +
        df[month_col].astype(str).str.zfill(2) + '-' +
        df[day_col].astype(str).str.zfill(2) + ' ' +
        df[hour_col].astype(str).str.zfill(2) + ':00:00',
        errors='coerce'
    )

    df = df.dropna(subset=['datetime'])
    df['month']       = df['datetime'].dt.month
    df['hour']        = df['datetime'].dt.hour
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df = df[df['ALLSKY_SFC_SW_DWN'] >= 0]

    features = ['month', 'hour', 'day_of_year', 'T2M']
    target   = 'ALLSKY_SFC_SW_DWN'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    return model

def predict(model, month, hour, day_of_year, temperature):
    new_data = pd.DataFrame({
        'month':       [month],
        'hour':        [hour],
        'day_of_year': [day_of_year],
        'T2M':         [temperature]
    })
    predicted = model.predict(new_data)[0]
    daily_kwh = predicted * 5 * 0.18 * 5
    return {
        "irradiance": round(predicted, 2),
        "peak_power_kw": round(predicted * 5 * 0.18, 2),
        "daily_kwh": round(daily_kwh, 2),
        "monthly_kwh": round(daily_kwh * 30, 2)
    }
