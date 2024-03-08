import requests
import math
import xmltodict
from flask import Flask, request, jsonify
from datetime import datetime
import logging
from geopy.geocoders import Nominatim

#Used ChatGPT to fix errors and understand flask, geopy

app = Flask(__name__)

response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
data = xmltodict.parse(response.content)

@app.route('/comment', methods=['GET'])
def ret_comment():
    """
    Returns the comment list from the data

    Returns:
       (list): The comment list from the data
    """
    return data['ndm']['oem']['body']['segment']['data']['COMMENT']

@app.route('/header', methods=['GET'])
def ret_header():
    """
    Returns the header dict from the data

    Returns:
       (dict): The header dict from the data
    """
    return data['ndm']['oem']['header']

@app.route('/metadata', methods=['GET'])
def ret_metadata():
    """
    Returns the metadata dict from the data

    Returns:
       (dict): The metadata dict from the data
    """
    return data['ndm']['oem']['body']['segment']['metadata']

@app.route('/epochs/<epoch>/location', methods=['GET'])
def inst_location(epoch):
    """
    Calculates and returns the latitude, longitude, altitude, and geoposition for a given epoch.

    Args:
        epoch (str): The epoch timestamp to calculate speed for

    Returns:
        loc (dict): Dictionary contianing the calculated latitude, longitude, altiude, and geoposition
    """
    try:
        datetime.strptime(epoch, "%Y-%jT%H:%M:%S.%fZ")
        valid_epoch = True
    except ValueError:
        valid_epoch = False
    if valid_epoch == False:
        return jsonify({"error": "Invalid epoch format. Please use YYYY-DDDTMM:SS.sssZ"}), 400

    epochs_list = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for i in epochs_list:
        if i['EPOCH'] == epoch:
            x = float(i['X']['#text'])
            y = float(i['Y']['#text'])
            z = float(i['Z']['#text'])

            epoch_string = epoch
            epoch_datetime = datetime.strptime(epoch_string, "%Y-%jT%H:%M:%S.%fZ")
            hrs = epoch_datetime.hour
            mins = epoch_datetime.minute

            MEAN_EARTH_RADIUS = 6378
            lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
            lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 19
            alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
            
            geocoder = Nominatim(user_agent='iss_tracker')
            geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')

            if geoloc == None:
                geoloc = "No location data"

            if lon > 180: lon = -180 + (lon - 180)
            if lon < -180: lon = 180 + (lon + 180)

            loc = {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "geoposition": geoloc
            }
    
            return loc
    
    return jsonify({"error": "Epoch not found"}), 404

@app.route('/now', methods=['GET'])
def current():
    """
    Calculates and returns the closest speed to the current time.

    Returns:
        speed (float): The calculated speed closest to the current time
    """
    
    timestamps = [datetime.strptime(i['EPOCH'], "%Y-%jT%H:%M:%S.%fZ") for i in data['ndm']['oem']['body']['segment']['data']['stateVector']]
    time_differences = [abs(x - datetime.now()) for x in timestamps]
    closest_index = time_differences.index(min(time_differences))

    closest_timestamp_data = data['ndm']['oem']['body']['segment']['data']['stateVector'][closest_index]
    logging.debug("Debug attempt, should be true: %s", closest_timestamp_data != None) #Debugging logging
    x_dot = float(closest_timestamp_data['X_DOT']['#text'])
    y_dot = float(closest_timestamp_data['Y_DOT']['#text'])
    z_dot = float(closest_timestamp_data['Z_DOT']['#text'])
    speed = math.sqrt(x_dot**2 + y_dot**2 + z_dot**2)
    
    x = float(closest_timestamp_data['X']['#text'])
    y = float(closest_timestamp_data['Y']['#text'])
    z = float(closest_timestamp_data['Z']['#text'])

    epoch_string = closest_timestamp_data['EPOCH']
    epoch_datetime = datetime.strptime(epoch_string, "%Y-%jT%H:%M:%S.%fZ")
    hrs = epoch_datetime.hour
    mins = epoch_datetime.minute
    

    MEAN_EARTH_RADIUS = 6378
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 19
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
            
    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')

    if geoloc == None:
        geoloc = "No location data"
    else:
        geoloc = str(geoloc)

    if lon > 180: lon = -180 + (lon - 180)
    if lon < -180: lon = 180 + (lon + 180)

    loc = {
        "latitude": lat,
        "longitude": lon,
        "altitude": alt,
        "geoposition": geoloc
    }

    return loc


@app.route('/epochs', methods=['GET'])
def print_data():
    """
    Prints a subset of state vector data based on provided limit and offset or prints the entire data set.
    Args:
        None (uses query parameters):
            limit (int): Maximum number of items to return
            offset (int): Index to start returning items from

    Returns:
        result (list of dicts): Set of state vector data
    """
    epochs_list = data['ndm']['oem']['body']['segment']['data']['stateVector']

    limit = request.args.get('limit', 0, type=int)
    offset = request.args.get('offset', 0, type=int)
    

    if limit != 0:
        try:
            limit = int(limit)
            offset = int(offset)
        except ValueError:
            return "Invalid input, must be integer"
        
        logging.debug("Debug attempt, should be true: %s", limit != None) 
        logging.debug("Debug attempt, should be true: %s", offset != None) 

        if (offset + limit) <= len(epochs_list):
            if offset == 0:
                result = epochs_list[offset:(offset + limit)]
            else:
                result = epochs_list[offset:((offset + limit)-1)]
            return result
        else:
            return "Invalid input, must be within data range"
    else:
        return epochs_list

@app.route('/epochs/<epoch>', methods=['GET'])
def print_epoch(epoch):
    """
    Prints the state vector data corresponding to a given epoch.

    Args:
        epoch (str): The epoch timestamp to retrieve data for

    Returns:
        x (dict): The state vector data for the given epoch
    """
    try:
        datetime.strptime(epoch, "%Y-%jT%H:%M:%S.%fZ")
        valid_epoch = True
    except ValueError:
        valid_epoch = False
    if valid_epoch == False:
        return jsonify({"error": "Invalid epoch format. Please use YYYY-DDDTMM:SS.sssZ"}), 400
    dataval = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for x in dataval:
        if x['EPOCH'] == epoch:
            return x

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def inst_speed(epoch):
    """
    Calculates and returns the instantaneous speed for a given epoch.

    Args:
        epoch (str): The epoch timestamp to calculate speed for

    Returns:
        speed (float): The calculated instantaneous speed
    """
    try:
        datetime.strptime(epoch, "%Y-%jT%H:%M:%S.%fZ")
        valid_epoch = True
    except ValueError:
        valid_epoch = False
    if valid_epoch == False:
        return jsonify({"error": "Invalid epoch format. Please use YYYY-DDDTMM:SS.sssZ"}), 400
    
    timestamp_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    logging.debug("Debug attempt, should be true: %s", timestamp_data != None) #Debugging logging
    for x in timestamp_data:
        if x['EPOCH'] == epoch:
            x_dot = float(x['X_DOT']['#text'])
            y_dot = float(x['Y_DOT']['#text'])
            z_dot = float(x['Z_DOT']['#text'])

            speed = math.sqrt(x_dot**2 + y_dot**2 + z_dot**2)

    return str(speed)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
