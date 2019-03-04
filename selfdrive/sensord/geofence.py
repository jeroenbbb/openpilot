# check geofence vs gps position
# and send result on zmq
# https://shapely.readthedocs.io/en/latest/manual.html#introduction
# IsGeofenceEnabled (0/1) and the GeoFence data are stored in params
# a geofence is stored in geojson format  OR kml file??
# for example:
# 
# see also https://stackoverflow.com/questions/16942697/geojson-circles-supported-or-not

#import shapely
from shapely.geometry import Polygon, Point, mapping, shape
import json

#print (shapely.__version__)

# read geofence from parameter file
# bloemendaal = 52.3992479,4.630414
#points = [(34.093523, -118.274893), (34.091414, -118.275887), (34.092082, -118.278062), (34.093867, -118.276609), (34.093523, -118.274893)]
#polygon = Polygon(points)

geojson = '{"type": "Polygon", "coordinates": [  [[30, 10], [40, 40], [20, 40], [10, 20], [30, 10]]   ]  }'
s = shape(json.loads(geojson))
print(json.dumps(mapping(s)))

d = Point(52.3992479,4.630414).distance(s)
print (d)

# the area in square degrees, usefull?
# area_sdeg = polygon.area

# get gps position from zmq
lat = 52.3992479
lon = 4.630414
speed = 5
bearing = 270

# check if position is within the fence


# predict next position using bearing and speed

# and check the predicted position

# and send results to zmq

# is separate prcoess because it is slow: display 
# import reverse_geocoder as rg
# coordinates = (51.5214588,-0.1729636),(9.936033, 76.259952),(37.38605,-122.08385)
# results = rg.search(coordinates) # default mode = 2
