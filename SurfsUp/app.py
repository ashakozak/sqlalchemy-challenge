# Import necessary libraries and modules
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


# Set up database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create references to the mapped tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Initialize the Flask app
app = Flask(__name__) 


# Home route displaying available API endpoints
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation <br/>"
        "Precipitation data for the last year<br/>"
        "/api/v1.0/stations <br/>"
        "List of weather stations<br/>"
        "/api/v1.0/tobs <br/>"
        "Temperature observations for the last year at the most active station<br/>"
        "/api/v1.0/start_date <br/>"
        "Temperature statistics from a specific start date<br/>"
        "/api/v1.0/start_date/end_date<br/>"
        "Temperature statistics for a date range<br/>"
         "start_date and end_date format: YYYY-MM-DD <br/>"
    )

# Endpoint to get precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>= query_date).all()  

    session.close()

    # Create a dictionary & return json with the date as the key and the value as the precipitation
    all = []
    for date, prcp in results:
        prcp_disct = {}
        prcp_disct["date"] = date
        prcp_disct["prcp"] = prcp
        
        all.append(prcp_disct)

    return jsonify(all)

# Endpoint to get data about the weather stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Join Station and Measurement tables and query the necessary fields
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation,\
                            Measurement.date, Measurement.prcp, Measurement.tobs).\
                            join(Measurement, Station.station == Measurement.station).\
                            order_by(Station.name).all()

    session.close()

    # Convert the query results into a dictionary and put into a list
    all_stations = []
    for station_id, name, latitude, longitude, date, prcp, tobs, elevation in results:
        station_dict = {}
        station_dict["station"] = station_id
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        station_dict["date"] = date
        station_dict["prcp"] = prcp
        station_dict["tobs"] = tobs
        all_stations.append(station_dict)

    return jsonify(all_stations)

# Endpoint to get temperature observations for the last year from a specific station
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and temperature
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date>= query_date).\
        filter(Measurement.station == "USC00519281").all()  

    session.close()

    # Convert the query results into a dictionary and put into a list
    all_tops = []
    for date, tobs in results:
        tobs_disct = {}
        tobs_disct["date"] = date
        tobs_disct["tobs"] = tobs
        all_tops.append(tobs_disct)

    # Convert the list of dictionnaries into a dictionnary 
    response = {
        "1": "Data for the most active station (USC00519281)",
        "2": all_tops
    }

    # Return json
    return jsonify(response)

# Endpoint to get temperature stats from a given start date till the end of the dataset    
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the min, max, and average temperatures calculated from the given \
    # start date to the end of the dataset
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).first()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).first()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).first()

    # Close the session
    session.close()

    # Return json
    return jsonify({
        "min_temp": min_temp[0],
        "max_temp": max_temp[0],
        "avg_temp": avg_temp[0]
    })

# Endpoint to get temperature stats between given start and end dates
@app.route("/api/v1.0/<start>/<end>")
def end_date(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the min, max, and average temperatures calculated from the given \
    # start date to the given end date    
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).\
                filter(Measurement.date<=end).first()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).\
                filter(Measurement.date<=end).first()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).\
                filter(Measurement.date<=end).first()
    
    # Close the session
    session.close()

    # Return json
    return jsonify({
        "min_temp": min_temp[0],
        "max_temp": max_temp[0],
        "avg_temp": avg_temp[0]
    })

   
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)