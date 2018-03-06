# Servo Control
#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
import socket
import StringIO
import time

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
count = 0
while (count < 10):
	NeckC+=10 
	RxC+=10
	s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
	time.sleep(0.5)
	count +=1
	while s.recv(2) != 'ok':
		print ("waiting...")
 
#s.close()
#LOOK AT ME!!!!!!
