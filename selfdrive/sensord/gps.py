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

# USB device numers:
# 1546  U-Blox AG
#	01a4  Antaris 4
#	01a5  [u-blox 5]
#	01a6  [u-blox 6]
#	01a7  [u-blox 7]
#	01a8  [u-blox 8]

# 8086 = Intel


import sys

if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")

import time
import zmq
import random

# gps3 uses gpsd
from gps3 import gps3
import usb1
from time import sleep

import selfdrive.messaging as messaging
from selfdrive.services import service_list
from common.basedir import BASEDIR
#from selfdrive.swaglog import cloudlog

# use message port number for GPS messages defined in 
# use message structure GpsLocationData defined in log.capnp and gpsLocationExternal in Event message
# service_list['gpsNMEA'].port                    # consist of a long string of NMEa data
# service_list['gpsLocationExternal'].port


#TODO changes this into import usb1

def list_usb_devices():
    with usb1.USBContext() as context:
        for device in context.getDeviceIterator(skip_on_error=True):
            print('ID %04x:%04x' % (device.getVendorID(), device.getProductID()), '->'.join(str(x) for x in ['Bus %03i' % (device.getBusNumber(), )] + device.getPortNumberList()), 'Device', device.getDeviceAddress())

    context = usb1.USBContext()
    #context.setDebug(9)

    for device in context.getDeviceList(skip_on_error=True):
        if device.getVendorID() == 0xbbaa and device.getProductID() == 0xddcc:
            
            handle = device.open()
            handle.claimInterface(0)
            # handle.controlWrite(0x40, 0xdc, SAFETY_ALLOUTPUT, 0, b'')

    dat = handle.controlRead(usb1.TYPE_VENDOR | usb1.RECIPIENT_DEVICE, 0xd2, 0, 0, 0x10)
    print (dat)

# old versdion based on pyusb    
def list_usb_devices_old():
    print ("List USB devices:")
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

# read all data from igc file into a list
# B H H M M S S D D M M M M M N D D D M M M M M E V P P P P P G G G G G CR LF
# Description Size Element Remarks
# Time 6 bytes HHMMSS Valid characters 0-9
# Latitude 8 bytes DDMMMMMN Valid characters N, S, 0-9
# Longitude 9 bytes DDDMMMMME Valid characters E,W, 0-9
# Fix valid 1 byte V A: valid, V:nav warning
# Press Alt. 5 bytes PPPPP Valid characters -, 0-9
# GPS Alt. 5 bytes GGGGG 
# example: B1433005223946N00437387EA0000800007

def read_igc_file():
    # print (BASEDIR)
    with open(BASEDIR + "/selfdrive/sensord/openpilot.igc") as f:
        content = f.readlines()
    return content

# search next line that start with a B
def read_next_line(content, count_igc_line):
    check_char = ""
    while check_char != "B":
        count_igc_line = count_igc_line + 1
        # at the end, start over again
        if count_igc_line >= len(content):
            count_igc_line = 1
        line = content[count_igc_line]
        check_char = line[:1]
    lat = float(line[ 7:14]) / 100000
    lon = float(line[15:23]) / 100000
    alt = int(line[25:30])
    # convert lat, lon from minutes to decimals 
    intPart, decimalPart = divmod(lat, 1)
    lat = intPart + decimalPart/60*100
    intPart, decimalPart = divmod(lon, 1)
    lon = intPart + decimalPart/60*100
    
    print (lat, lon, alt)
    return lat, lon, count_igc_line
# -------------------------------
list_usb_devices()
igc_content = read_igc_file()


def main(gctx=None):

    # set gpsd stuff
    gpsd_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gpsd_socket.connect()
    gpsd_socket.watch()
    
    count = 0
    count_igc_line = 0

    # set message stuff
    context = zmq.Context()
    gps_sock = messaging.pub_sock(context, service_list['gpsLocationExternal'].port)

    for new_data in gpsd_socket:
        if new_data:
            data_stream.unpack(new_data)
            latitude = data_stream.TPV['lat']
            longitude = data_stream.TPV['lon']

            print('Altitude = ',data_stream.TPV['alt'])
            print('Latitude = ',latitude)
            print('Lon = ',longitude)
            print (isinstance(latitude, float))
            
            if not isinstance(latitude, float): 
                latitude, longitude, speed, accuracy, bearing = make_some_dummy_data ()
                latitude, longitude, count_igc_line = read_next_line(igc_content,count_igc_line)
                
        else:
            # noting received, send some dummy data
            # print ("Nothing" + str(count))
            latitude, longitude, speed, accuracy, bearing = make_some_dummy_data ()
            latitude, longitude, count_igc_line = read_next_line(igc_content,count_igc_line)
    
        sleep(0.5)
        count = count + 1
    
        # send message
        msg = messaging.new_message()
        msg.init('gpsLocationExternal')
        msg.gpsLocationExternal.latitude = latitude
        msg.gpsLocationExternal.longitude = longitude
        msg.gpsLocationExternal.speed = speed
        msg.gpsLocationExternal.bearing = bearing
        msg.gpsLocationExternal.accuracy = accuracy
        msg.gpsLocationExternal.source = "external"
        msg.gpsLocationExternal.flags = 1
        gps_sock.send(msg.to_bytes())
        #cloudlog.info ("Message sent: " + str(latitude) + " " + str(longitude))

        
if __name__ == "__main__":
  main()    
