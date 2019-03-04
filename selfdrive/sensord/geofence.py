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
from shapely.ops import nearest_points
import json
mport geopy.distance



from shapely import speedups
if speedups.available:
  speedups.enabled

#print (shapely.__version__)

# read geofence from parameter file
# bloemendaal = 52.3992479,4.630414
#points = [(34.093523, -118.274893), (34.091414, -118.275887), (34.092082, -118.278062), (34.093867, -118.276609), (34.093523, -118.274893)]
#polygon = Polygon(points)

geojson = '{"type": "Polygon", "coordinates": [  [[52, 4.7], [52, 5], [53, 5], [53, 4.7], [52, 4.7]]   ]  }'
geojson2 = {"type": "Polygon", "coordinates": [  [[53, 4], [53, 5], [54, 5], [54, 4], [53, 4]]   ]  }
s = shape(json.loads(geojson))
s2 = shape(geojson2)
print(json.dumps(mapping(s)))

d = Point(52.0, 4.0).distance(s)
print (d)

d = Point(52.0 ,4.0).distance(s2)
print (d)

d = nearest_points(Point(52.0,4.0), s2)
print (d[0])
print (d[1])
print (d[0].x)
print (d[0].y)

coords_1 = (52.0, 4.0)
coords_2 = (53.0, 5.0)

print geopy.distance.vincenty(coords_1, coords_2).km

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
