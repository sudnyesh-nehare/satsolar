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
    year_col  = next((v for k,v in cols_lower.items() if 'year' in k), None)
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

    irradiance = model.predict(new_data)[0]

    # correct calculations for a 5kW system
    system_kw        = 5.0
    efficiency       = 0.18
    panel_area_m2    = system_kw * 1000 / (1000 * efficiency)  # ~27.7 m²
    peak_power_kw    = (irradiance * panel_area_m2 * efficiency) / 1000
    peak_power_kw    = min(peak_power_kw, system_kw)
    sun_hours        = 5.5
    daily_kwh        = peak_power_kw * sun_hours
    monthly_kwh      = daily_kwh * 30

    # money savings (avg ₹8 per kWh in India)
    monthly_savings  = monthly_kwh * 8

    # location rating based on irradiance
    if irradiance >= 600:
        rating = 5
        rating_text = "Excellent"
    elif irradiance >= 450:
        rating = 4
        rating_text = "Very Good"
    elif irradiance >= 300:
        rating = 3
        rating_text = "Good"
    elif irradiance >= 150:
        rating = 2
        rating_text = "Average"
    else:
        rating = 1
        rating_text = "Poor"

    # recommendation
    if irradiance >= 450:
        advice = "Your location gets strong sunlight. Installing a rooftop solar system is a smart investment!"
        should_install = True
    elif irradiance >= 200:
        advice = "Your location gets moderate sunlight. Solar panels can still work well, especially between 10am and 2pm."
        should_install = True
    else:
        advice = "Sunlight is low at this hour. Try checking between 10am and 2pm for better results."
        should_install = False

    return {
        "irradiance":       round(irradiance, 1),
        "peak_power_kw":    round(peak_power_kw, 2),
        "daily_kwh":        round(daily_kwh, 2),
        "monthly_kwh":      round(monthly_kwh, 1),
        "monthly_savings":  round(monthly_savings, 0),
        "rating":           rating,
        "rating_text":      rating_text,
        "advice":           advice,
        "should_install":   should_install
    }
