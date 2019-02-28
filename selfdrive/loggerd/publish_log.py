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

    context = zmq.Context()
    service_sock = []
        
    # loop through all services to define socks
    for service in service_list:
        print (service)
        print (service_list[service].port)
        service_sock[service] = messaging.sub_sock(context, service_list[service].port)

    # loop through all services to listen to the socks
    while True:
        for service in service_list:
            msg = messaging.recv_sock(service_sock[service], wait=False)
            if msg is not None:
                print (service + "=" + msg)
        time.sleep(1)

if __name__ == "__main__":
    listen_to_all()
