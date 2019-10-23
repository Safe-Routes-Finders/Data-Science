from decouple import config
from flask import Flask, render_template, request
from .model import latlontoarea
import numpy as numpy
import pandas as pd
import joblib
from lightgbm import LGBMClassifier
import category_encoders as ce
from sklearn.pipeline import make_pipeline



def create_app():
    app = Flask(__name__)
    @app.route('/')
    def hello():
        """Basic Hello World to verify connection works"""
        return "Hello World"
    
    @app.route('/predict', methods=['POST'])
    @app.route('/predict/<lat>/<lon>/<hour>/<dow>/', methods=['GET'])
    def predict(lat=None,lon=None,hour=None,dow=None):
        """
        Takes a Lat, Lon, Hour, and Day of Week, and Returns probability an accident will occur.
        EXAMPLE QUERY:
        http://127.0.0.1:5000/predict/33.3427/-118.3258/200/4/
        returns: 0.15845681340644727
        """
        #parsing values from the URL into python variables
        lat = (lat or request.values['lat'])
        lon = (lon or request.value['lon'])
        hour = (hour or request.value['hour'])
        dow = (dow or request.value['dow'])
        hour = int(hour)
        dow = int(dow)
        #queries the sql database to find out what area of the city a lat/lon is in
        area_name = latlontoarea(lat,lon)
        
        #creates a dummy prediction dataframe, passing in the name of the area, the hour of the day, and the day of week
        pred = pd.DataFrame(
            columns=['area_name', 'hour_time', 'dayofweek'],
            data=[[area_name,hour,dow]]
        )

        #loads in the category encoder pipeline
        pipeline = joblib.load('pipeline.joblib')
        
        #transforms the area name to the category encoder
        pred_transformed = pipeline.transform(pred)

        #loads in Vishnu's logistic model
        model = joblib.load('logistic.joblib')
        
        #runs the transformed prediction through vishnu's model to return the probabilty an accident occurs
        y_pred = model.predict_proba(pred_transformed)[0][1]
        #returns it as a string to populate on page
        return str(y_pred)

    return app
