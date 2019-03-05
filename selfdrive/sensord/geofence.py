# check geofence vs gps position
# and send result on zmq
# https://shapely.readthedocs.io/en/latest/manual.html#introduction
# IsGeofenceEnabled (0/1) and the GeoFence data are stored in params
# a geofence is stored in geojson format
# see also https://stackoverflow.com/questions/16942697/geojson-circles-supported-or-not
#
# this program reads the geofences from tha param file and the gps location from zmq
# it uses shapely to find the nearest point and distance
# if the distance=0, the gps location is in the fence
#   using the bearing and speed, the next point after 1 second is estimated and again checked against the fence
# else it uses geopy to calculate the distance between the 2 points
# if current-point and future-point are within the fence, geofence = green
# if current-point is in the fence but future point not, geofence = orange
# if current-point and future-point are outside the fence, geofence = red
# the gps accurancy is taken into account

import sys
from shapely.geometry import Polygon, Point, mapping, shape
from shapely.ops import nearest_points
import json
import geopy.distance

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import zmq
import selfdrive.messaging as messaging
from selfdrive.services import service_list
from common.params import Params
from selfdrive.swaglog import cloudlog

from shapely import speedups
if speedups.available:
  speedups.enabled


# bloemendaal = 52.3992479,4.630414
#points = [(34.093523, -118.274893), (34.091414, -118.275887), (34.092082, -118.278062), (34.093867, -118.276609), (34.093523, -118.274893)]
#polygon = Polygon(points)

#geojson = '{"type": "Polygon", "coordinates": [  [[52, 4.7], [52, 5], [53, 5], [53, 4.7], [52, 4.7]]   ]  }'
#geojson2 = {"type": "Polygon", "coordinates": [  [[53, 4], [53, 5], [54, 5], [54, 4], [53, 4]]   ]  }
#geojson3 = {"type": "Polygon", "coordinates": [  [[52, 5], [52, 6], [53, 6], [53, 5], [52, 5]]   ]  }
#s = shape(json.loads(geojson))
#s2 = shape(geojson2)

#print(json.dumps(mapping(s)))

# read geofence from parameter file
params = Params()
geofence = params.get("GeoFence")
is_geofence_enabled = params.get("IsGeofenceEnabled") == '1'

if geofence == '':
  is_geofence_enabled = False
  
if is_geofence_enabled:
  try:
    geofence_shape = shape(geofence)
  except TopologicalError:
    is_geofence_enabled = False
    cloudlog.info('Incorrect GeoJSON found in param file')

print (is_geofence_enabled)


# read gps stuff from zmq
context = zmq.Context()
gps_sock = messaging.sub_sock(context, service_list['gpsLocationExternal'].port)
msg = messaging.recv_sock(gps_sock, wait=False)


# calculate distance between current position and geofence(s)
d = Point(52.0, 4.0).distance(geofence_shape)

# calculate the nearest point between 
d = nearest_points(Point(52.0,4.0), s3)
print (d[0])
print (d[1])
print (d[0].x)
print (d[0].y)

print ("Geopy distance in meters")
coords_1 = (52.0, 4.0)
coords_2 = (53.0, 4.0)
print (geopy.distance.distance(coords_1, coords_2).m)

print ("Geopy distance in meters")
coords_1 = (52.0, 4.0)
coords_2 = (52.0, 5.0)
print (geopy.distance.distance(coords_1, coords_2).m)

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
