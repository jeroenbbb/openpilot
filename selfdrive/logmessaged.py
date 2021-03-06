#!/usr/bin/env python
import zmq
from logentries import LogentriesHandler
from selfdrive.services import service_list
import selfdrive.messaging as messaging

# this program reads all messages from ipc (Inter Process Comm).
# IPC is using a file to transfer messages, /tmp/logmessage
# the messages are sent by selfdrive.swaglog.py
# logmessage is used by loggerd, swaglog.c, swaglog.py, sensord
# all ipc messages are forwarded to zmq by logmessaged.py
# severe stuff (more than info) are sent to logentries which is a central cloudbased logging database
# logentries is skipped in this version


def main(gctx):
  # setup logentries. we forward log messages to it
  le_token = "e8549616-0798-4d7e-a2ca-2513ae81fa17"
  le_handler = LogentriesHandler(le_token, use_tls=False, verbose=False)

  le_level = 20 #logging.INFO

  ctx = zmq.Context()
  sock = ctx.socket(zmq.PULL)
  sock.bind("ipc:///tmp/logmessage")

  # and we publish them
  pub_sock = messaging.pub_sock(ctx, service_list['logMessage'].port)

  while True:
    # changed in python3, no more auto conversion from bytes to string
    #dat = ''.join(sock.recv_multipart())
    dat = b''.join(sock.recv_multipart())
    dat = dat.decode('ascii')
    

    # print "RECV", repr(dat)

    levelnum = ord(dat[0])
    dat = dat[1:]

    if levelnum >= le_level:
      # push to logentries does not work with emit_raw (LogentriesHandler object has no object emit_raw)
      # so skip it
      # le_handler.emit_raw(dat)
      pass

    # then we publish them
    msg = messaging.new_message()
    msg.logMessage = dat
    pub_sock.send(msg.to_bytes())

if __name__ == "__main__":
  main(None)
