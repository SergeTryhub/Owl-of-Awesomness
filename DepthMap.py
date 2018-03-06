#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
import socket
import cv2
import StringIO
import time
import keyboard

TCP_IP = '10.0.0.10'
TCP_PORT = 12345
BUFFER_SIZE = 24
#s.close()

RxC=1530 
RyC=1560
LxC=1420
LyC=1440 
NeckC=1530
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
#s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))

#camera matrix
LeftMat=[[582.39100314, 0, 299.87247641],
         [0, 581.86742884, 215.57217382],
         [0, 0, 1]]

LeftDist=[0.09225191, -0.40577916, -0.00708927, -0.0050356, 0.5408364]

RightMat=[[590.61725106, 0, 288.20236937],
         [0, 589.41015463, 228.98459041],
         [0, 0, 1]]

RightDist=[0.05790892, -0.41533829, -0.00990576, -0.00553869, 3.12468689]

while True:
    #get image, split and assign to left and right
    cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
    ret, img = cap.read()
    cv2.imshow("image", img)
    img1 = img[0:480,  0:640]       #left
    img2 = img[0:480,  640:1280]   #right
    cv2.waitKey(30)

    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    disparity = stereo.compute(imgL,imgR)
    plt.imshow(disparity,'gray')
    plt.show()
