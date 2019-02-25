import pyqtgraph
import socket

import numpy as np

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:"

    print type(data)

    string = [string.replace('[', '').replace(']', '').replace('\n', '')[1:] for string in data.split(']')][0]
    print string.replace('...', '')
    print np.fromstring(string, sep=' ')
    #print[np.fromstring(string.replace('[', '').replace(']', '').replace('\n', '')[1:], sep='.  ', dtype=np.int32) for string in data.split(']')]
