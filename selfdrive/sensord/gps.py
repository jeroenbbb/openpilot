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
        print ("  dev: " + str(dev.dev.bNumConfigurations))
        
