# Fantastic Mr. ISS
### The following files read through the ISS data set XML file using flask routes containerized in a Docker file and summarizes  different statistics within their files. This allows for an easier read of the basic components found within the file. 
### Included Files
1. `iss_tracker.py`

This file reads includes 8 different functions:

  `print_data`: This function returns the entire dataset; accepts query parameters for specific data ranges.
  
  `print_epoch`: This function takes an epoch string via Flask route and returns its state vector.
  
  `inst_speed`: This function accepts an epoch string via Flask route and returns its speed.
  
  `ret_comment`: This function returns the ‘comment’ list from the data set.
  
  `ret_header`: This function returns the ‘header’ dict object from ISS data
  
  `ret_metadata`: This function returns the ‘metadata’ dict object from ISS data
  
  `inst_location`: This function returns the latitude, longitude, altitude, and geoposition for the Epoch that is nearest in time
  
  `current`: This function returns instantaneous speed, latitude, longitude, altitude, and geoposition for the Epoch that is nearest in time.


2. `test_iss_tracker.py`
   
  This file contains the unit tests for iss_tracker.py
  
3. `Dockerfile`

    The Dockerfile is a recipe for creating a Docker image containing a sequential set of commands (a recipe) for installing and configuring the application.
    
4. `diagram.png`
   
    This file includes the software diagram for homework05.
   
5. `docker-compose.yml`
   
  The docker compose simplifies the management of multi-container Docker applications using rules defined in a YAML file
  
6. `requirements.txt`
    
  The requirements file contains all the non-standard Python libraries essential for our application.

### Diagram
![diagram_](https://github.com/rheasamuel12/iss_tracker/assets/143050090/5f874700-7cf2-46ba-b32f-dde04bffb9d9)
This diagram illustrates the sequence of components within the project, including the User, Jetstream VM, Docker Container, Flask, Python files, and the NASA database. It visually explains how each component interacts with one another.
### Building Instructions
Make sure you have docker and flask installed before starting. To build the python scripts type

`docker-compose build`

### Running/Building Instructions
In the command line type
`docker-compose up -d`

to start the container in the background.

To run each route:
1. `curl localhost:5000/epochs`

Returns the entire data set

2. `curl "localhost:5000/epochs?limit=int&offset=int"`

Returns modified list of Epochs given query parameters. Make sure to replace `int` with a integer value.

3. `curl localhost:5000/epochs<epoch>`

Returns state vectors for a specific Epoch from the data set. Make sure to replace `<epoch>` with the epoch of your choice.

4. `curl localhost:5000/epochs<epoch>/speed`

Returns the speed for a specific Epoch from the data set. Make sure to replace `<epoch>` with the epoch of your choice.


5. `curl localhost:5000/now`

Returns instantaneous speed, latitude, longitude, altitude, and geoposition for the Epoch that is nearest in time

6. `curl localhost:5000/comment`

Returns ‘comment’ list object from ISS data


7. `curl localhost:5000/metadata`

Returns ‘metadata’ dict object from ISS data


8. `curl localhost:5000/header`

  Returns ‘header’ dict object from ISS data


9.  `curl localhost:5000/epochs<epoch>/location`

   Returns latitude, longitude, altitude, and geoposition for a specific Epoch in the data set.  Make sure to replace `<epoch>` with the epoch of your choice.
### Unit Testing
To run the unit tests, simply type:

`pytest test/test_iss_tracker.py` 

in the terminal.

Once you are ready to stop the container, type:

`docker-compose down`

### Sample Code
```
 MEAN_EARTH_RADIUS = 6378
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 19
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
            
    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')
```
This code is from the current() function in the iss_tracker.py script. It uses the epoch closest to the current time and uses its x,y,z coordinates to find the latitude, longitude, altitude, and geolocation according to these equations. 
### Sample Results
Using this route `curl localhost:5000/now`, the following output occurs.
```
{
  "altitude": 416.737983668394,
  "geoposition": "No location data",
  "latitude": -23.467204976731693,
  "longitude": 89.03060611549562
}
```

To test another route, I could call `curl localhost:5000/epochs/2024-074T12:00:00.000Z`. The following output occurs:
```
{
  "EPOCH": "2024-074T12:00:00.000Z",
  "X": {
    "#text": "4361.0105068273897",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "2.25603844265299",
    "@units": "km/s"
  },
  "Y": {
    "#text": "-392.52963816617802",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "7.1858437146965803",
    "@units": "km/s"
  },
  "Z": {
    "#text": "-5202.6075373420399",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "1.35323694656583",
    "@units": "km/s"
  }
}
```
### Citations
ISS data: https://spotthestation.nasa.gov/trajectory_data.cfm

Real Time ISS Position: https://www.n2yo.com/?s=90027

Geopy Docs: https://geopy.readthedocs.io/en/stable/#

API for Real Time ISS Position: http://api.open-notify.org/iss-now.json
