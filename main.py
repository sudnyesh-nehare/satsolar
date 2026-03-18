from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime
from model import fetch_and_train, predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# cache trained models by location
model_cache = {}

class PredictRequest(BaseModel):
    latitude: float
    longitude: float
    hour: int
    temperature: float

@app.get("/")
def root():
    return {"status": "SatSolar API is running!"}

@app.post("/predict")
def get_prediction(req: PredictRequest):
    # round to 1 decimal to reuse nearby locations
    cache_key = (round(req.latitude, 1), round(req.longitude, 1))

    if cache_key not in model_cache:
        model_cache[cache_key] = fetch_and_train(req.latitude, req.longitude)

    model = model_cache[cache_key]

    now = datetime.datetime.now()
    month      = now.month
    day_of_year = now.timetuple().tm_yday

    result = predict(model, month, req.hour, day_of_year, req.temperature)
    return result
