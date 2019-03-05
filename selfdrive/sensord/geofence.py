# check geofence vs gps position
# and send result on zmq
#
# this program reads the geofences from the param file and the gps location from zmq
#   IsGeofenceEnabled (0/1) and the GeoFence data are stored in params
#   a geofence is stored in geojson format
#   the zmq message = gpsLocationExternal

# it uses shapely to find the nearest point and distance
#   see https://shapely.readthedocs.io/en/latest/manual.html#introduction
# if the distance=0, the gps location is in the fence
#   using the bearing and speed, the next point after 1 second is estimated and again checked against the fence
# it uses geopy to calculate the distance between the 2 points
# if current-point and future-point are within the fence, geofence = green
# if current-point is in the fence but future point not, geofence = orange
# if current-point and future-point are outside the fence, geofence = red
# the gps accurancy is taken into account

# is separate prcoess because it is slow: display 
# import reverse_geocoder as rg
# coordinates = (51.5214588,-0.1729636),(9.936033, 76.259952),(37.38605,-122.08385)
# results = rg.search(coordinates) # default mode = 2

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
from common import realtime

from shapely import speedups
if speedups.available:
  speedups.enabled

# testdata
# bloemendaal = 52.3992479,4.630414
# points = [(34.093523, -118.274893), (34.091414, -118.275887), (34.092082, -118.278062), (34.093867, -118.276609), (34.093523, -118.274893)]
# polygon = Polygon(points)
# geojson = '{"type": "Polygon", "coordinates": [  [[52, 4.7], [52, 5], [53, 5], [53, 4.7], [52, 4.7]]   ]  }'
# geojson2 = {"type": "Polygon", "coordinates": [  [[53, 4], [53, 5], [54, 5], [54, 4], [53, 4]]   ]  }
# geojson3 = {"type": "Polygon", "coordinates": [  [[52, 5], [52, 6], [53, 6], [53, 5], [52, 5]]   ]  }
# s = shape(json.loads(geojson))
# s2 = shape(geojson2)
# print(json.dumps(mapping(s)))
#geofence = {"xxxx/34"}
#geofence = {"type": "Polygon", "coordinates": [  [[52, 5], [52, 6], [53, 6], [53, 5], [52, 5]]   ]  }

def read_geofence():
    # read geofence from parameter file nad convert to string, enabled=1 means True
    params = Params()
    geofence = params.get("GeoFence").decode()
    is_geofence_enabled = params.get("IsGeofenceEnabled").decode() == '1'

    # print (params.get("IsFcwEnabled").decode())
    # print (geofence)

    if geofence == '':
        is_geofence_enabled = False

    if is_geofence_enabled:
        try:
        # convert the string into a dict and create a shape in shapely
            geofence_dict = json.loads(geofence)
            geofence_shape = shape(geofence_dict)
        except AttributeError:
            is_geofence_enabled = False
            cloudlog.info('GeoJSON from param file could not be converted into a shape')
        except JSONDecodeError:
            is_geofence_enabled = False
            cloudlog.info('Incorrect GeoJSON found in param file')

    return is_geofence_enabled, geofence_shape
        

#------ main routine --------
is_geofence_enabled, geofence_shape = read_geofence()
context = zmq.Context()
gps_sock = messaging.sub_sock(context, service_list['gpsLocationExternal'].port)
start_time = int(realtime.sec_since_boot())
print (start_time)

# loop forever
while True:
    while is_geofence_enabled:
        # get gps position from zmq
        lat = 52.3992479
        lon = 4.630414
        speed = 5
        bearing = 270

        msg = messaging.recv_sock(gps_sock, wait=True)
        latitude  = msg.gpsLocationExternal.latitude
        longitude = msg.gpsLocationExternal.longitude
        speed     = msg.gpsLocationExternal.speed
        accuracy  = msg.gpsLocationExternal.accuracy

        # calculate distance between current position and geofence(s)
        d = Point(latitude, longitude).distance(geofence_shape)

        # calculate the nearest point between 
        d = nearest_points(Point(latitude,longitude), geofence_shape)
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
        coords_1 = ( d[0].x, d[0].y )
        print (geopy.distance.distance(coords_1, coords_2).m)

        # check if position is within the fence

        # predict next position using bearing and speed

        # and check the predicted position

        # and send results to zmq
        
    # check the params file every 5 mins because it might have been changed
    is_geofence_enabled, geofence_shape = read_geofence()
