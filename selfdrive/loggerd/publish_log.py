# read all messages from zmq
# and send them to a website using POST
# the website may store and publish them
# also respond to request from Telegram
# telegram.py is listening to Telegram requests so the function is started in a thread

import time
import zmq
import sys
import requests
import threading

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import selfdrive.messaging as messaging
import selfdrive.loggerd.telegram as telegram
from selfdrive.services import service_list
from cereal import log

# display all services
for service in service_list:
    print (service)
    print (service_list[service].port)

# set upload time interval for every message
# name, number of seconds between 2 uploads
upload_interval = {
    "gpsLocationExternal": 5,
    "navUpdate": 30,
    "logMessage": 120,
    "health": 300,
    "thermal": 30,
    "liveMapData": 30
}

# define list for all last uploads
last_upload = {}

# define list to remeber last message so it can be communicated to Telegram
last_message = {}

def upload(msgtype, data):
    url = "https://esfahaniran.com/openpilot/index.php"
    post_fields = {'type': msgtype, 'data': data}
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    try:
        # = requests.post(url, data=post_fields, headers=header,timeout=5)
        r = requests.post(url, data=post_fields, timeout=5)
        # json = urlopen(request).read().decode()
        # r = requests.post(url, data={'data': data, 'type': msgtype})
        print(r.status_code, r.reason)
        print(r.text)
    except:
        print ("Timeout, no upload")

# check priority, not every message has to be uploaded every time
# and some special fields can be extracted from the message
# see cereal/log.capnp - struct Event for all possible messages

def define_upload_required(evnt):
    
    field1 = ""
    field2 = ""
    upload_required = False
    
    type = evnt.which()
    if type == 'gpsLocationExternal':
        # get gps locations 
        field1 = evnt.gpsLocationExternal.latitude
        field2 = evnt.gpsLocationExternal.longitude
        
    # check time in sec since last upload
    if type in last_upload:
        time_since_last_upload = (evnt.logMonoTime - last_upload[type]) / 1000000000
    else:
        time_since_last_upload = 1000
    # print (time_since_last_upload)
    if type in upload_interval:
        if upload_interval[type] < time_since_last_upload:
            # priority of message type is higher than the last upload
            # so a next upload is required
            print ("Upload required")
            upload_required = True
            last_upload[type] = evnt.logMonoTime

    return upload_required, field1, field2


def telegramd_thread():
    global last_message
    telegram.main()
    
    
def main(gctx=None):

    context = zmq.Context()
    poller = zmq.Poller()    
    service_sock =  []
    count = 0
    
    # start telegram stuff
    #telegram_thread = threading.Thread(target=telegramd_thread)
    #telegram_thread.daemon = True
    #telegram_thread.start()
    count = 0
    last_update_id = None
    print (telegram.get_me())

    
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
            print(evt.which())
            
            # remember last message for every message type
            last_message[evt.which()] = print(evt, flush=False)
            
            # check if the message has to be uploaded or not 
            upload_required, field1, field2 = define_upload_required(evt)
            if evt.which() == 'liveMapData':
                print(evt)
 
            if priority == 10:
                upload(evt.which(), evt)
                priority = 0
                
        # check if Telegram is asking something
        updates = telegram.get_updates(last_update_id)
        print (updates)
        if len(updates["result"]) > 0:
            last_update_id = telegram.get_last_update_id(updates) + 1
            telegram.handle_answer(updates, last_message)
        time.sleep(2)
        print ("Sleep" + str(count))
        count = count + 1
        
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
