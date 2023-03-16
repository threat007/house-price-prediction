# House Price Prediction

This microservice predicts house price based on property parameters longitude,latitude,housing_median_age,total_rooms,total_bedrooms,population,households,median_income

### Environment Variables
```
PREDICTED_DATA_FILE_NAME -> This is complete path for the file which is being used as cache for the predicted house prices 
MODEL_FILE -> This is a model file trained and generated to be used as engine to predict house prices based on the housing paramters
``` 
### Prerequisites to run this project locally
1. Install docker in your system
2. Start the docker application

### How to run the application locally
1. Checkout this project into your local machine using git checkout command or directly download as zip file from the git repository
2. Open a terminal or a command window
3. Navigate to the root folder of the project i.e ../house-price-prediction/
4. Run command "docker build -t house_price_prediction_image ." --> This command builds docker Image
5. Run command "docker run -d --name house_price -p 80:80 house_price_prediction_image" --> This command runs the container with the image we built earlier
6. Now you can access the API documentations using the url : http://localhost/docs
7. Open api json can be accessed at  http://localhost/openapi.json

### How to run tests locally
1. Install python (3.9.13 version) in your local system
2. To make sure python is installed run command python -V in a command window or terminal
3. Navigate to the tests folder of the project i.e ../house-price-prediction/tests/
4. Run command pip3 install -r ../requirements_test.txt
5. Run command "python -m pytest"