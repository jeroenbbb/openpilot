# read gps data from a usb gps
# using nmea and gpsd
# http://doschman.blogspot.com/2013/01/parsing-nmea-sentences-from-gps-with.html
# https://raspberrytips.nl/ublox-neo-6m-gps-raspberry-pi-3/
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/

# http://www.catb.org/gpsd/
# http://www.catb.org/gpsd/gpsd_json.html
# http://www.catb.org/gpsd/hardware.html

# https://github.com/Knio/pynmea2
# http://www.linux-usb.org/usb.ids  lists all vendors, product id in hex
# https://en.wikipedia.org/wiki/USB#Device_classes   (devclass 9 = hub)
# https://stackoverflow.com/questions/6146131/python-gps-module-reading-latest-gps-data#6146351
# https://github.com/MartijnBraam/gpsd-py3
# http://catb.org/gpsd/
# http://ozzmaker.com/using-python-with-a-gps-receiver-on-a-raspberry-pi/

import sys

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import time
import zmq
import random

# gps3 uses gpsd
from gps3 import gps3
import usb
from time import sleep

import selfdrive.messaging as messaging
from selfdrive.services import service_list

# use message port number for GPS messages defined in 
# use message structure GpsLocationData defined in log.capnp and gpsLocationExternal in Event message
# service_list['gpsNMEA'].port                    # consist of a long string of NMEa data
# service_list['gpsLocationExternal'].port



def list_usb_devices():
    busses = usb.busses()
    for bus in busses:
        print (vars(bus))
        devices = bus.devices
        for dev in devices:
            print ("Device:", dev.filename)
            print ("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
            print ("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
            print ("  devnum: " + str(dev.iManufacturer) + str(dev.devnum))
            print ("  deviceClass: " + str(dev.dev.bDeviceClass))
            print ("  dev: " + str(dev.dev))
            
# -------------------------------
list_usb_devices()

gpsd_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gpsd_socket.connect()
gpsd_socket.watch()
count = 0

# set message stuff
context = zmq.Context()
gps_sock = messaging.pub_sock(context, service_list['gpsLocationExternal'].port)
msg = messaging.new_message()
msg.init('gpsLocationExternal')
    
for new_data in gpsd_socket:
    if new_data:
        data_stream.unpack(new_data)
        latitude = data_stream.TPV['lat']
        print('Altitude = ',data_stream.TPV['alt'])
        print('Latitude = ',latitude)
        if not isinstance(latitude, float): 
            latitude=float(5)
    else:
        # noting received, send some dummy data
        print ("Nothing" + str(count))
        latitude = float(52.3992479) + random.random(-0.1, 0.1)
        longitude = float(4.630414) + random.random(-0.1, 0.1)
        speed = float(5) + random.random()
        
    
    sleep(0.5)
    count = count + 1
    
    # send message
    msg.gpsLocationExternal.latitude = latitude
    msg.gpsLocationExternal.longitude = longitude
    msg.gpsLocationExternal.source = "external"
    gps_sock.send(msg.to_bytes())
    
