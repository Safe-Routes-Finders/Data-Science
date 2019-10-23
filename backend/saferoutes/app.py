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
        return "Hello World"
    
    @app.route('/predict', methods=['POST'])
    @app.route('/predict/<lat>/<lon>/<hour>/<dow>/', methods=['GET'])
    def predict(lat=None,lon=None,hour=None,dow=None):
        lat = (lat or request.values['lat'])
        lon = (lon or request.value['lon'])
        hour = (hour or request.value['hour'])
        dow = (dow or request.value['dow'])
        hour = int(hour)
        dow = int(dow)
        area_name = latlontoarea(lat,lon)
        
        
        
        
        
        pred = pd.DataFrame(
            columns=['area_name', 'hour_time', 'dayofweek'],
            data=[[area_name,hour,dow]]
        )
        pipeline = joblib.load('pipeline.joblib')
        
        pred_transformed = pipeline.transform(pred)
        model = joblib.load('logistic.joblib')
        
        y_pred = model.predict_proba(pred_transformed)[0][1]
        #import pdb; pdb.set_trace()
        try:
            if request.method =='GET':
                message = 'The pin is located at {} and {}'.format(lat,lon)
        except Exception as e:
            message = 'Error adding {}: {}'.format(lat,e)
            pass
        return str(y_pred)

    return app
