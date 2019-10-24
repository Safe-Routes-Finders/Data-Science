from decouple import config
from flask import Flask, render_template, request
from .model import latlontoarea,single_prediction,prediction_24hrs,prediction_allareas
import numpy as numpy
import pandas as pd

from lightgbm import LGBMClassifier
import category_encoders as ce
from sklearn.pipeline import make_pipeline
import os,json



def create_app():
    app = Flask(__name__)
    #getting the site path
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    data_url = os.path.join(SITE_ROOT, "data")
    
    @app.route('/')
    def hello():
        """Basic Hello World to verify connection works"""
        return "Hello World"
    
    @app.route('/predict/<lat>/<lon>/<predicttime>/', methods=['GET'])
    def predict(lat=None,lon=None,predicttime=None):
        """
        Takes a Lat, Lon, Hour, and Day of Week, and Returns probability an accident will occur.
        EXAMPLE QUERY:
        http://127.0.0.1:5000/predict/33.3427/-118.3258/200/4/
        returns: 0.15845681340644727
        """
        #parsing values from the URL into python variables
        lat = (lat or request.values['lat'])
        lon = (lon or request.value['lon'])
        predict_time = (predicttime or request.value['predicttime'])
        y_pred = single_prediction(lat,lon,predict_time)
        
        return str(y_pred)

    @app.route('/predict24hrs/<lat>/<lon>/<predicttime>/', methods=['GET'])
    def predict24hrs(lat=None,lon=None,predicttime=None):
        """
        Takes a Lat, Lon, Hour, and Day of Week, and Returns probability an accident will occur.
        EXAMPLE QUERY:
        http://127.0.0.1:5000/predict/33.3427/-118.3258/200/4/
        returns: 0.15845681340644727
        """
        #parsing values from the URL into python variables
        lat = (lat or request.values['lat'])
        lon = (lon or request.value['lon'])
        predict_time = (predicttime or request.value['predicttime'])
        y_pred = prediction_24hrs(lat,lon,predict_time)
        
        return str(y_pred)

    @app.route('/predictallareas/<predicttime>/', methods=['GET'])
    def allareas(predicttime=None):
        """
        Takes a Lat, Lon, Hour, and Day of Week, and Returns probability an accident will occur.
        EXAMPLE QUERY:
        http://127.0.0.1:5000/predict/33.3427/-118.3258/200/4/
        returns: 0.15845681340644727
        """
        #parsing values from the URL into python variables
        predict_time = (predicttime or request.value['predicttime'])
        y_pred = prediction_allareas(predict_time)
        
        return str(y_pred)

    return app
