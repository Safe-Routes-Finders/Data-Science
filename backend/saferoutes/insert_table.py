import psycopg2
from sqlalchemy import create_engine
import pandas as pd

#Reading area_latlon file to upload into pandas
area_latlon = pd.read_csv('cleaned_area_latlon.csv')
#Print the shape of area_latlon and print the top 5 rows
print(area_latlon.shape)
print(area_latlon.head())
#Pring the columns of the area_latlon dataframe
print(area_latlon.columns)

from sqlalchemy import create_engine

dbname = "eskdnyfr"
username = "eskdnyfr"
pass_word = "NlXqx6b6NMw30uvGubKWK-NOx2mEuddF"
host = "salt.db.elephantsql.com"
#creating creating engine inserting the area_latlon dataframe to postgres
try:
    engine = create_engine(f'postgresql://{username}:{pass_word}@{host}/{username}')
    area_latlon.to_sql('area_latlon_v2', engine)
except:
    pass

# pg_connect = psycopg2.connect(dbname=dbname, user=username,
#                                 password=pass_word, host=host)
# cur = pg_connect.cursor()