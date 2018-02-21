# Servo Control
#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
import socket
#import cv2
import StringIO
 
TCP_IP = '10.0.0.10'
TCP_PORT = 12345
BUFFER_SIZE = 24
 
RxC=1530 
RyC=1560
LxC=1420
LyC=1440 
NeckC =1530
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
 
s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
while s.recv(2) != 'ok':
 print ("waiting...")
 
#s.close()
#LOOK AT ME!!!!!!
