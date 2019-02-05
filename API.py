import numpy as np
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from datetime import datetime

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

YearStart = dt.datetime(2016,8,23) 
YearEnd = dt.datetime(2017,8,24)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def percipitation():

	prcpresults = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date > YearStart).filter(Measurement.date < YearEnd).all()

	Oneyear_dates = []
	Oneyear_prcp = []

	for r in prcpresults:
		Oneyear_dates.append(r[0])

	for r in prcpresults:
		Oneyear_prcp.append(r[1])

	prcpresults_DF = pd.DataFrame({'Date':Oneyear_dates, 'Percipitation': Oneyear_prcp})
	prcpresults_DF = prcpresults_DF.sort_values(by='Date', ascending=True )

	# turn df to  dictionary 
	json_prcpresults = prcpresults_DF.to_dict(orient='split')
    
    #Return the json representation of your dictionary.
	return jsonify({'status': 'ok', 'json_data': json_prcpresults})

@app.route("/api/v1.0/stations")
def station():

	stations_names = session.query(Station.station, Station.name, Station.latitude,Station.longitude,Station.elevation).statement
	stations_names_DF = pd.read_sql_query(stations_names, session.bind)

	json_stations_DF = stations_names_DF.to_dict(orient='split')
	return jsonify({'status': 'ok', 'json_data': json_stations_DF})

@app.route("/api/v1.0/tobs")
def tabs():

    tabs= session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > YearStart).filter(Measurement.date < YearEnd).statement
    
    Tabs_read_sql = pd.read_sql_query(tabs, session.bind)

    Tabs_json = Tabs_read_sql.to_dict(orient='split')
    #Return the json representation of your dictionary.
    return jsonify({'status': 'ok', 'json_data': Tabs_json})

@app.route('/api/v1.0/<start>')
@app.route("/api/v1.0/<start>/<end>")
def start_temp(start,end=''):
    start = datetime.strptime(start,'%Y-%m-%d')
    if(end=='') :
        end= datetime.today()
    else : 
        end = datetime.strptime(end,'%Y-%m-%d')
    vaca_starend=session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
                    filter(Measurement.date>=start).\
                    filter(Measurement.date<=end).\
                    all()
    temp_dict={}
    temp_dict["max"]= vaca_starend[0][0]
    temp_dict["min"]=vaca_starend[0][1]
    temp_dict["avg"]=vaca_starend[0][2]

    
    return  jsonify(temp_dict) 

if __name__ == '__main__':
	app.run(debug=True)

