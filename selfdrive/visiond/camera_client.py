# this program sends images to a server
# see https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/?__s=ks7cs5jn9uwghuvfttga
# needs  
# pip install opencv-contrib-python
# pip install zmq
# pip install imutils
# git clone https://github.com/jeffbass/imagezmq.git
#   cd ~/lib/python3.5/site-packages
#   ln -s ~/imagezmq/imagezmq imagezmq

from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())
 
# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
	args["server_ip"]))
  
# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()
#vs = VideoStream(src=0).start()
time.sleep(2.0)
 
while True:
	# read the frame from the camera and send it to the server
	frame = vs.read()
	sender.send_image(rpiName, frame)  
