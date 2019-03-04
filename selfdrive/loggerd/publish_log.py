# read all messages from zmq
# and send them to a website using POST
# the website may store and publish them

import time
import zmq
import sys

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import selfdrive.messaging as messaging
from selfdrive.services import service_list

# display all services
for service in service_list:
    print (service)
    print (service_list[service].port)
    

def listen_to_all():

    context = zmq.Context()
    service_sock =  []
    count = 0
        
    # loop through all services to define socks
    for service in service_list:
        print (service)
        print (service_list[service].port)
        service_sock.append(messaging.sub_sock(context, service_list[service].port))
        # count = count + 1

    # loop through all services to listen to the socks

    while True:
        count = 0
        for service in service_list:
            msg = messaging.recv_sock(service_sock[count], wait=False)
            if msg is not None:
                if isinstance(msg, str):
                    print (service + "=" + msg)
                else:
                    print ("message received from " + service + " " + str(msg))
                    #type(msg)
            count = count + 1
        
        time.sleep(1)

if __name__ == "__main__":
    listen_to_all()
