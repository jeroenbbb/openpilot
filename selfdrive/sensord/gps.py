# read gps data from a usb gps
# using nmea and gpsd
# http://doschman.blogspot.com/2013/01/parsing-nmea-sentences-from-gps-with.html
# https://raspberrytips.nl/ublox-neo-6m-gps-raspberry-pi-3/
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
# http://www.catb.org/gpsd/
# http://www.catb.org/gpsd/hardware.html
# https://github.com/Knio/pynmea2

import usb
busses = usb.busses()
for bus in busses:
    devices = bus.devices
    for dev in devices:
        print ("Device:", dev.filename)
        print ("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
        print ("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
        print ("  iMan: " + str(dev.iManufacturer) + str(dev.bConfigurationValue))
        

for dev in usb.core.find(find_all=True):
    print (dev.get_active_configuration())
    print ("Device:", dev.filename)
    print ("  idVendor: %d (%s)" % (dev.idVendor, hex(dev.idVendor)))
    print ("  idProduct: %d (%s)" % (dev.idProduct, hex(dev.idProduct)))
