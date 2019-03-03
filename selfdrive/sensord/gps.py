# read gps data from a usb gps
# using nmea and gpsd
# http://doschman.blogspot.com/2013/01/parsing-nmea-sentences-from-gps-with.html
# https://raspberrytips.nl/ublox-neo-6m-gps-raspberry-pi-3/
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
# http://www.catb.org/gpsd/
# http://www.catb.org/gpsd/hardware.html
# https://github.com/Knio/pynmea2
# http://www.linux-usb.org/usb.ids  lists all vendors, product id in hex
# https://en.wikipedia.org/wiki/USB#Device_classes   (devclass 9 = hub)
# https://stackoverflow.com/questions/6146131/python-gps-module-reading-latest-gps-data#6146351
# https://github.com/MartijnBraam/gpsd-py3
# http://catb.org/gpsd/
# http://ozzmaker.com/using-python-with-a-gps-receiver-on-a-raspberry-pi/

import usb
busses = usb.busses()
for bus in busses:
    print (vars(bus))
    devices = bus.devices
    for dev in devices:
        #dev.__dict__.keys()
        #print (vars(dev))
        print ("Device:", dev.filename)
        print ("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
        print ("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
        print ("  devnum: " + str(dev.iManufacturer) + str(dev.devnum))
        print ("  deviceClass: " + str(dev.dev.bDeviceClass))
        print ("  dev: " + str(dev.dev))
        
        try:
            dev.dev.set_configuration()
        except USBError:
            print ("USB authorisation error, use sudo chgrp users /dev/bus/usb/001/*")
            
# -------------------------------
import threading
import time
from gps import *

class GpsPoller(threading.Thread):

   def __init__(self):
       threading.Thread.__init__(self)
       self.session = gps(mode=WATCH_ENABLE)
       self.current_value = None

   def get_current_value(self):
       return self.current_value

   def run(self):
       try:
            while True:
                self.current_value = self.session.next()
                time.sleep(0.2) # tune this, you might not get values that quickly
       except StopIteration:
            pass

if __name__ == '__main__':

   gpsp = GpsPoller()
   gpsp.start()
   # gpsp now polls every .2 seconds for new data, storing it in self.current_value
   while 1:
       # In the main thread, every 5 seconds print the current value
       time.sleep(5)
       print gpsp.get_current_value() 

    
#------------------------    
from gps3 import gps3
gpsd_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gpsd_socket.connect()
gpsd_socket.watch()
for new_data in gpsd_socket:
    if new_data:
        data_stream.unpack(new_data)
        print('Altitude = ',data_stream.TPV['alt'])
        print('Latitude = ',data_stream.TPV['lat'])
        
