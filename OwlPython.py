#!/usr/bin/env python

import socket
import cv2

TCP_IP = '10.0.0.10'
TCP_PORT = 22
BUFFER_SIZE = 1024
#MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
#s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()
cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
if (cap.isOpened()==False):
    print "no video"
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        cv2.imshow('Frame',frame)
    else:
        print "broke"
print "received data:", data
