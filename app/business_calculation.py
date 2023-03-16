import datetime
import logging
import os
from enum import Enum

import joblib
import pandas as pd


class Columns(Enum):
    LONGITUDE = 'longitude'
    LATITUDE = 'latitude'
    HOUSING_MEDIAN_AGE = 'housing_median_age'
    TOTAL_ROOMS = 'total_rooms'
    TOTAL_BEDROOMS = 'total_bedrooms'
    POPULATION = 'population'
    HOUSEHOLDS = 'households'
    MEDIAN_INCOME = 'median_income'
    OCEAN_PROXIMITY = 'ocean_proximity'
    PREDICTED_VALUE = 'predicted_value'
    TIMESTAMP = 'timestamp'


logger = logging.getLogger(__name__)


def extract_predicted_value_from_data_file(housing, settings):
    data_frame = pd.read_csv(settings.PREDICTED_DATA_FILE_NAME)
    predicted_value = None
    time_stamp = None
    if not pd.isnull(data_frame).empty:
        # filter file data with the input values to get predicted value
        filtered_data_frame = data_frame.loc[
            (data_frame[Columns.LONGITUDE.value] == housing.longitude) &
            (data_frame[Columns.LATITUDE.value] == housing.latitude) &
            (data_frame[Columns.HOUSING_MEDIAN_AGE.value] == housing.housing_median_age) &
            (data_frame[Columns.TOTAL_ROOMS.value] == housing.total_rooms) &
            (data_frame[Columns.TOTAL_BEDROOMS.value] == housing.total_bedrooms) &
            (data_frame[Columns.POPULATION.value] == housing.population) &
            (data_frame[Columns.HOUSEHOLDS.value] == housing.households) &
            (data_frame[Columns.MEDIAN_INCOME.value] == housing.median_income) &
            (data_frame[Columns.OCEAN_PROXIMITY.value] == housing.ocean_proximity)]
        if not pd.isnull(filtered_data_frame[Columns.PREDICTED_VALUE.value]).empty:
            predicted_value = filtered_data_frame.values[0][9]
            time_stamp = filtered_data_frame.values[0][10]
    return predicted_value, time_stamp


def predict_housing_value_and_cache(housing, settings):
    try:
        columns = [col.value for col in Columns]
        columns.remove(Columns.PREDICTED_VALUE.value)
        columns.remove(Columns.TIMESTAMP.value)
        data = [[housing.longitude, housing.latitude, housing.housing_median_age, housing.total_rooms,
                 housing.total_bedrooms, housing.population, housing.households, housing.median_income,
                 housing.ocean_proximity]]
        df = pd.DataFrame(data=data, columns=columns)
        model = load_model(settings.MODEL_FILE)
        predicted_value = predict(df, model)
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        update_data_file(predicted_value, housing, current_time, settings)
    except Exception as ex:
        print(ex)
        raise ex
    return predicted_value, current_time


def update_data_file(predicted_value, housing, current_time, settings):
    data = [[housing.longitude, housing.latitude, housing.housing_median_age, housing.total_rooms,
             housing.total_bedrooms, housing.population, housing.households, housing.median_income,
             housing.ocean_proximity, predicted_value, current_time]]
    df = pd.DataFrame(data=data, columns=[col.value for col in Columns])
    df.to_csv(settings.PREDICTED_DATA_FILE_NAME, mode='a', index=False, header=False)
    logger.info(f'Data file updated with data {data}')


def create_predicted_data_file(settings):
    """
    creates an empty csv file in project directory named PREDICTED_DATA_FILE
    this file stores the predicted housing value for every request
    """
    file_exists = os.path.exists(settings.PREDICTED_DATA_FILE_NAME)
    if not file_exists:
        columns = [col.value for col in Columns]
        data_frame = pd.DataFrame(columns=columns)
        data_frame.to_csv(settings.PREDICTED_DATA_FILE_NAME, index=False)
        logger.info(f"Data file created with columns:{columns}")


def predict(df, model):
    new_columns = ['ocean_proximity_<1H OCEAN', 'ocean_proximity_INLAND', 'ocean_proximity_ISLAND',
                   'ocean_proximity_NEAR BAY', 'ocean_proximity_NEAR OCEAN']
    last_column_name = df.iloc[:, -1][0]
    modified_data_frame = df.drop(df.columns[-1], axis=1)
    column_value_dict = {}
    for column in new_columns:
        if last_column_name in column:
            value = 1
        else:
            value = 0
        column_value_dict[column] = value

    column_no = 8
    for column, value in column_value_dict.items():
        try:
            modified_data_frame.insert(column_no, column=column, value=value)
            column_no = column_no + 1
        except ValueError:
            logger.info("column already exists")

    predicted_value_list = model.predict(modified_data_frame)
    if len(predicted_value_list) > 0:
        return predicted_value_list[0]
    else:
        logger.error(f"error while getting prediction for data: {df}")
        raise Exception("Prediction failed")


def load_model(filename):
    try:
        model = joblib.load(filename)
    except Exception as ex:
        logger.error(f"error while loading model: {ex}")
        raise ex
    return model
