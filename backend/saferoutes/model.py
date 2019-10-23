import pandas as pd
import psycopg2

dbname = "eskdnyfr"
username = "eskdnyfr"
pass_word = "password"
host = "salt.db.elephantsql.com"

#takes a lat lon and returns the Area Name
#DEPRECATED for pipeline category encoder
def latlontoarea(lat,lon):
    connection = psycopg2.connect(user=username,password=pass_word,host=host, port="5432", database=dbname)
    cursor = connection.cursor()
    query = '''SELECT "Area Name" FROM "area_latlon"  WHERE lat = ''' +str(lat)+ "AND lon = " + str(lon)
    cursor.execute(query)
    area = cursor.fetchall()[0][0]
    return area