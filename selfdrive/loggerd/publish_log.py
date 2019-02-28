# read all messages from zmq
# and send them to a website using POST
# the website may store and publish them

import time
import zmq
import sys

sys.path.append("/home/pi/openpilot")

import selfdrive.messaging as messaging
from selfdrive.services import service_list

# display all services
for service in service_list:
    print (service)
    print (service_list[service].port)
    

def listen_to_all():
    # port = "12344"       
    context = zmq.Context()
    thermal_sock = messaging.sub_sock(context, service_list['thermal'].port)
    msg = messaging.recv_sock(thermal_sock, wait=True)
    print (msg)

if __name__ == "__main__":
    listen_to_all()
