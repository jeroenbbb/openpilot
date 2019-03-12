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
    poller = zmq.Poller()
    
    # loop through all services to define socks
    for service in service_list:
        print (service)
        print (service_list[service].port)
        port = service_list[service].port
        # service_sock.append(messaging.sub_sock(context, service_list[service].port))
        sock = messaging.sub_sock(context, port, poller)
        # count = count + 1

    # define poller to listen to all sockets
    
    #for i in range(0,count):
    #    poller.register( service_sock[i],  zmq.POLLIN )

    # poll all incoming messages
    while True:
        #socks = dict( poller.poll())
        print ("1")
        polld = poller.poll(timeout=1000)
        print ("2")
        for sock in polld:
            print ("3")
            #msg = sock.recv()
            msg = sock.recv_multipart()
            print (str(msg))
        # find the correct socket
        #if socket in socks and socks[socket] == zmq.POLLIN:
        #    msg = socket.recv_multipart()
        
    # loop through all services to listen to the socks    
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
