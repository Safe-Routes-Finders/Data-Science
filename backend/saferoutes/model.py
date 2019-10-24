import pandas as pd
import psycopg2
import joblib
import os
from datetime import datetime,timedelta
from decouple import config

#setting the values of variables
dbname = config('DBNAME')
username = config('USERNAME')
pass_word = config('PASSWORD')
host = config('HOST')
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
data_url = os.path.join(SITE_ROOT, "data")
pipeline = joblib.load(data_url+'/pipeline.joblib')
model = joblib.load(data_url+'/lgbmmodel.joblib')
predict_set = pd.read_csv(data_url+'/predict_set.csv')
predict_set24hours = pd.read_csv(data_url+'/predict_set24hours.csv')
features = predict_set.columns.drop(['date_hour','date_accident'])

def getprediction(data):
    """ Sending positive prediction probailities """
    #Transforming the predict data using the pipeline encoder
    data_transformed = pipeline.transform(data[features])
    #Getting the probabilit of a crash for the given Lat long and datetime
    predictions = model.predict_proba(data_transformed)[:,1]
   
    return predictions


def latlontoarea(lat,lon):
    connection = psycopg2.connect(user=username,password=pass_word,host=host, port="5432", database=dbname)
    cursor = connection.cursor()
    query = '''SELECT "Area Name" FROM "area_latlon"  WHERE lat = ''' +str(lat)+ "AND lon = " + str(lon)
    cursor.execute(query)
    area = cursor.fetchall()[0][0]
    return area



def single_prediction(lat,lon,predict_time):
    """ Returns the probability of a crash at the current time.
        Using Latitude, Longitude and Date Time 
     """   
    #queries the sql database to find out what area of the city a lat/lon is in
    try:
        area_name = latlontoarea(lat,lon)
        #setting up the datapoints for prediction of a crash
        predict_data = predict_set[predict_set.area_name==area_name].copy()
        predict_time = pd.to_datetime(predict_time)
        predict_data['hour_time'] = (predict_time.hour)*100 #set the hour time for which you are predicting the crash
        predict_data['day']  = predict_time.day#set the value of the day
        predict_data['month'] = predict_time.month# set the value of the month
        predict_data['dayofweek'] = predict_time.dayofweek#set the value of the day of the week
        y_pred = getprediction(predict_data)
        
    except Exception as e:
        #Error due to lat long not available to Los Angeles area
        print(e)
        y_pred = "Prediction for Los Angeles Intersections only"
    
    return y_pred


def prediction_24hrs(lat,lon,predict_time):
    """ Returns the probability of a crash at the current time.
        Using Latitude, Longitude and Date Time 
     """   
    #queries the sql database to find out what area of the city a lat/lon is in
    try:
        area_name = latlontoarea(lat,lon)
        #setting up the datapoints for prediction of a crash
        data_24hrs = []
        predict_data = predict_set24hours[predict_set24hours.area_name==area_name].copy().reset_index(drop=True)
        initial_time = pd.to_datetime(predict_time)
        pred_times = []
        #creating predict data for the next 24 hours
        for i in range(24):
            predict_time =initial_time + timedelta(hours=i)
            pred_times.append(predict_time)
            predict_data.loc[i,'hour_time'] = (predict_time.hour)*100 #set the hour time for which you are predicting the crash
            predict_data.loc[i,'day']  = predict_time.day#set the value of the day
            predict_data.loc[i,'month'] = predict_time.month# set the value of the month
            predict_data.loc[i,'dayofweek'] = predict_time.dayofweek#set the value of the day of the week
            
        crash_probability = getprediction(predict_data)
        #creating a dataframe to send a json object
        crash_24hrs = pd.DataFrame({'Date Time':pred_times,'Crash Probability':crash_probability})
        y_pred = crash_24hrs.to_json(orient='records')
    except Exception as e:
        #Error due to lat long not available to Los Angeles area
        print(e)
        y_pred = {"Error":"Prediction for Los Angeles Intersections only"}
    
    return y_pred

def prediction_allareas(predict_time):
    """ Returns the probability of a crash at the current time.
        Using Latitude, Longitude and Date Time 
     """   
    #queries the sql database to find out what area of the city a lat/lon is in
    try:
        #setting up the datapoints for prediction of a crash for all areas
        predict_data = predict_set.copy()
        predict_time = pd.to_datetime(predict_time)
        predict_data['hour_time'] = (predict_time.hour)*100 #set the hour time for which you are predicting the crash
        predict_data['day']  = predict_time.day#set the value of the day
        predict_data['month'] = predict_time.month# set the value of the month
        predict_data['dayofweek'] = predict_time.dayofweek#set the value of the day of the week
        crash_probability = getprediction(predict_data)
        #creating a dataframe to send json object
        predict_areas = predict_data['area_name'].values
        crash_areas = pd.DataFrame({'area_name':predict_areas,'probability':crash_probability}).sort_values('probability').reset_index(drop=True)
        crash_categories = ['low' for i in range(7)]+['medium' for i in range(7)]+ ['high' for i in range(7)]
        crash_areas['category']=crash_categories
        y_pred = crash_areas.to_json(orient='records')
        
    except Exception as e:
        #Error due to lat long not available to Los Angeles area 
        y_pred = {"Error":"Prediction for Los Angeles Intersections only"}
    
    return y_pred
