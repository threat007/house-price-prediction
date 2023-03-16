import json

import pytest
from fastapi.testclient import TestClient

from app.business_calculation import create_predicted_data_file
from app.config import Settings
from app.main import app as main_app, get_settings

client = TestClient(main_app)


def get_settings_override():
    return Settings(PREDICTED_DATA_FILE_NAME='predicted_data.csv',
                    MODEL_FILE='model.joblib')


main_app.dependency_overrides[get_settings] = get_settings_override


@pytest.fixture(scope="session", autouse=True)
def startup_event():
    settings = get_settings_override()
    create_predicted_data_file(settings)


def test_fetch_all_prediction_history():
    response = client.get("/prediction-history")
    assert response.status_code == 200


def test_predict_house_price():
    response = client.post(
        "/predict-price",
        json={
            "longitude": -122.64,
            "latitude": 38.01,
            "housing_median_age": 36.0,
            "total_rooms": 1336.0,
            "total_bedrooms": 258.0,
            "population": 678.0,
            "households": 249.0,
            "median_income": 5.5789,
            "ocean_proximity": "NEAR OCEAN"
        },
    )
    assert response.status_code == 200
    response_json = json.dumps(response.json())
    assert 'predicted_value' in response_json
