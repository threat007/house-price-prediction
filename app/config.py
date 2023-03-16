from pydantic import BaseSettings


class Settings(BaseSettings):
    PREDICTED_DATA_FILE_NAME: str = 'app/data/predicted_data.csv'
    MODEL_FILE: str = 'app/model/model.joblib'

    class Config:
        env_file = ".env"
