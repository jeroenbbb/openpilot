#!/usr/bin/env python

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
from selfdrive.swaglog import cloudlog

# use message port number for GPS messages defined in 
# use message structure GpsLocationData defined in log.capnp and gpsLocationExternal in Event message
# service_list['gpsNMEA'].port                    # consist of a long string of NMEa data
# service_list['gpsLocationExternal'].port


#TODO changes this into import usb1
def list_usb_devices():
    busses = usb.busses()
    for bus in busses:
        print (vars(bus))
        devices = bus.devices
        for dev in devices:
            #print ("Device:", dev.filename)
            #print ("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
            #print ("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
            #print ("  devnum: " + str(dev.iManufacturer) + str(dev.devnum))
            #print ("  deviceClass: " + str(dev.dev.bDeviceClass))
            #print ("  dev: " + str(dev.dev))
            a = 1
            
def make_some_dummy_data ():
    latitude = float(52.3992479) + random.uniform(-0.001, 0.001)
    longitude = float(4.630414) + random.uniform(-0.001, 0.001)
    latitude = float(52) + random.uniform(-0.001, 0.001)
    longitude = float(5) + random.uniform(-0.001, 0.001)
    speed = float(5) + random.random()    
    accuracy = float(2) + random.uniform(1,10)
    bearing = float(0) + random.uniform(1,360)
    return latitude, longitude, speed, accuracy, bearing
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

def main(gctx=None):
    for new_data in gpsd_socket:
        if new_data:
            data_stream.unpack(new_data)
            latitude = data_stream.TPV['lat']
            longitude = data_stream.TPV['lon']
            print('Altitude = ',data_stream.TPV['alt'])
            print('Latitude = ',latitude)
            if not isinstance(latitude, float): 
                latitude, longitude, speed, accuracy, bearing = make_some_dummy_data ()
        else:
            # noting received, send some dummy data
            # print ("Nothing" + str(count))
            latitude, longitude, speed, accuracy, bearing = make_some_dummy_data ()
    
        sleep(0.5)
        count = count + 1
    
        # send message
        msg.gpsLocationExternal.latitude = latitude
        msg.gpsLocationExternal.longitude = longitude
        msg.gpsLocationExternal.speed = speed
        msg.gpsLocationExternal.bearing = bearing
        msg.gpsLocationExternal.accuracy = accuracy
        msg.gpsLocationExternal.source = "external"
        gps_sock.send(msg.to_bytes())
        #cloudlog.info ("Message sent: " + str(latitude) + " " + str(longitude))

        
if __name__ == "__main__":
  main()    
