# check geofence vs gps position
# and send result on zmq

#import shapely
from shapely.geometry import Polygon

#read geofence from parameter file
points = [(34.093523, -118.274893), (34.091414, -118.275887), (34.092082, -118.278062), (34.093867, -118.276609), (34.093523, -118.274893)]
polygon = Polygon(points)

# the area in square degrees, usefull?
# area_sdeg = polygon.area

# get gps position from zmq

# check if position is within the fence

# predict next position using bearing and speed

# and check the predicted position

# and send results to zmq
