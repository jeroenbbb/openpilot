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
    

def main(gctx=None):

    context = zmq.Context()
    service_sock =  []
    count = 0
        
    # loop through all services to define socks
    for service in service_list:
        print (service)
        # print (service_list[service].port)
        service_sock.append(messaging.sub_sock(context, service_list[service].port))
        # count = count + 1

    # loop through all services to listen to the socks
    poller = zmq.Poller()
    poller.register( service_sock[1],  zmq.POLLIN )
    
    while True:
        count = 0
        for service in service_list:
            # read all messages form this socket
            msg = messaging.recv_sock(service_sock[count], wait=False)
            while msg is not None:
                if isinstance(msg, str):
                    print (service + "=" + msg)
                else:
                    print ("message received from " + service + " " + str(msg))
                    #type(msg)
                msg = messaging.recv_sock(service_sock[count], wait=False)
            count = count + 1
        
        time.sleep(5)

if __name__ == "__main__":
    main()
