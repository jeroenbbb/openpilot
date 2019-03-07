# check geofence vs gps position
# and send result on zmq
#
# this program reads the geofences from the param file and the gps location from zmq
#   IsGeofenceEnabled (0/1) and the GeoFence data are stored in params
#   a geofence is stored in geojson format
#   the zmq message with GPS data = gpsLocationExternal
#   the zmq message for the result is navUpdate

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

def read_gps():
    msg = messaging.recv_sock(gps_sock, wait=True)
    latitude  = msg.gpsLocationExternal.latitude
    longitude = msg.gpsLocationExternal.longitude
    speed     = msg.gpsLocationExternal.speed
    bearing   = msg.gpsLocationExternal.bearing
    accuracy  = msg.gpsLocationExternal.accuracy
    
    #bearing should be in degrees
    #speed in m/s
    
    return latitude, longitude, speed, bearing, accuracy
    

def calculate_distance(latitude, longitude, geofence_shape):
    # calculate distance between current position and geofence(s)
    # distance = 0 means within the fence
    distance = Point(latitude, longitude).distance(geofence_shape)

    # calculate the nearest point between
    nearest_point = nearest_points(Point(latitude,longitude), geofence_shape)

    # and calculate the distance
    if distance != 0:
        coords_1 = ( nearest_point[0].x, nearest_point[0].y )
        coords_2 = ( nearest_point[1].x, nearest_point[1].y )
        distance = geopy.distance.distance(coords_1, coords_2).m
        
    print ("Geopy distance in meters: " + str(distance))
    return distance

    
#------ main routine --------
is_geofence_enabled, geofence_shape = read_geofence()
context = zmq.Context()
gps_sock = messaging.sub_sock(context, service_list['gpsLocationExternal'].port)
msg_sock = messaging.pub_sock(context, service_list['navUpdate'].port)
msg = messaging.new_message()
msg.init('navUpdate')
nav_update_segments = msg.navUpdate.init('segments',1)
start_time = int(realtime.sec_since_boot())

# loop forever
while True:
    while is_geofence_enabled:
        
        # get gps position from zmq
        latitude, longitude, speed, bearing, accuracy = read_gps()

        # calculate distance between current position and geofence(s)
        distance = calculate_distance(latitude, longitude, geofence_shape)

        # predict next position using bearing and speed
        origin = geopy.Point(latitude, longitude)
        future_point = geopy.distance.distance(meters=speed).destination(origin,bearing)
        
        # calculate distance between future position and geofence(s)
        future_distance = calculate_distance(future_point.latitude, future_point.longitude, geofence_shape)

        # and define geofence results
        result = "red"
        if distance == 0 and future_distance == 0:
            result = "green"
        if distance == 0 and future_distance > 0:
            result = "orange"
        if distance > future_distance:
            result = "orange"
        print (result)

        # and send results to zmq using NavigationMessage
        # type= 1
        # messageId = 1
        # data = geofence + result
        nav_update_segments[0].from = 1
        msg.navUpdate.segments[0].from = 1
        msg.navUpdate.isNavigating = True
        #msg.navUpdate.to = 
        #"geofence " + result
        msg_sock.send(msg.to_bytes())

        
    # check the params file every 5 mins because it might have been changed
    if start_time < int(realtime.sec_since_boot()) - 300:
        is_geofence_enabled, geofence_shape = read_geofence()
        start_time = int(realtime.sec_since_boot())
        print ("Re-read geofence from param")
