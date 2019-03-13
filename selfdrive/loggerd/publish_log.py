# read all messages from zmq
# and send them to a website using POST
# the website may store and publish them

import time
import zmq
import sys
import requests
#from urllib.parse import urlencode
#from urllib.request import Request, urlopen

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import selfdrive.messaging as messaging
from selfdrive.services import service_list
from cereal import log

# display all services
for service in service_list:
    print (service)
    print (service_list[service].port)

def upload(msgtype, data):
    url = "https://esfahaniran.com/openpilot/openpilot.php"
    post_fields = {'foo': 'bar'}     # Set POST fields here
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    try:
        r = requests.post(url, data=post_fields, headers=header,timeout=5)
        # json = urlopen(request).read().decode()
        # r = requests.post(url, data={'data': data, 'type': msgtype})
        print(r.status_code, r.reason)
    except:
        print ("Timeout, no upload")

def main(gctx=None):

    context = zmq.Context()
    poller = zmq.Poller()    
    service_sock =  []
    count = 0
    
    # loop through all services to define socks
    for service in service_list:
        print (service)
        print (service_list[service].port)
        port = service_list[service].port
        # service_sock.append(messaging.sub_sock(context, service_list[service].port))
        sock = messaging.sub_sock(context, port, poller)
        # count = count + 1

    # define poller to listen to all sockets
    # for i in range(0,count):
    #    poller.register( service_sock[i],  zmq.POLLIN )

    # poll all incoming messages
    priority = 1
    while True:

        polld = poller.poll(timeout=1000)

        for sock, mode in polld:
            #print (str(sock))
            #print (mode)
            msg = sock.recv()
            # msg = sock.recv_multipart()
            # print (str(msg))
            # print (msg.decode("ascii"))
            evt = log.Event.from_bytes(msg)
            print (evt)
            print(evt.which())

            # check if this message has to uploaded
            # check_priority
            
            if priority == 1:
                upload(evt, evt.which())
                priority = 0
        
    # loop through all services to listen to the socks    
    #while True:
    #    count = 0
    #    for service in service_list:
    #        # read all messages form this socket
    #        msg = messaging.recv_sock(service_sock[count], wait=False)
    #        while msg is not None:
    #            if isinstance(msg, str):
    #                print (service + "=" + msg)
    #            else:
    #                print ("message received from " + service + " " + str(msg))
    #                #type(msg)
    #            msg = messaging.recv_sock(service_sock[count], wait=False)
    #        count = count + 1
        
    #    time.sleep(5)

if __name__ == "__main__":
    main()
