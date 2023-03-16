import csv
import logging
from functools import lru_cache

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI

from app import config
from app.business_calculation import predict_housing_value_and_cache, create_predicted_data_file, Columns, \
    extract_predicted_value_from_data_file
from app.housing import Housing

app = FastAPI()
load_dotenv()
logger = logging.getLogger(__name__)


@lru_cache()
def get_settings():
    return config.Settings()


@app.on_event("startup")
def create_file():
    settings = get_settings()
    create_predicted_data_file(settings)


@app.get("/prediction-history")
def fetch_all_prediction_history(settings: config.Settings = Depends(get_settings)):
    columns = [col.value for col in Columns]
    try:
        with open(settings.PREDICTED_DATA_FILE_NAME) as file:
            rows = csv.DictReader(file, fieldnames=columns)
            data = [Housing(**row) for index, row in enumerate(rows) if index > 0]
        logger.info(f"Predicted data history: {data}")
    except FileNotFoundError as er:
        logger.error(f"File {settings.PREDICTED_DATA_FILE_NAME} not found")
        raise er
    return data


@app.post("/predict-price")
def predict_house_price(housing: Housing, settings: config.Settings = Depends(get_settings)):
    predicted_value, time_stamp = extract_predicted_value_from_data_file(housing, settings)
    if predicted_value is None:
        # calculate using predict function and save it to the file
        predicted_value, time_stamp = predict_housing_value_and_cache(housing, settings)
    housing.predicted_value = predicted_value
    housing.timestamp = time_stamp
    return housing
