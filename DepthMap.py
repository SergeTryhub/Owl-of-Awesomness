#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
import socket
import cv2
import StringIO
import time
import keyboard
import numpy
from matplotlib import pyplot as plt

TCP_IP = '10.0.0.10'
TCP_PORT = 12345
BUFFER_SIZE = 24
#s.close()

RxC=1460 
RyC=1560
LxC=1540
LyC=1470 
NeckC=1530
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))

#camera matrix
LeftMat=[[582.39100314, 0, 299.87247641],
         [0, 581.86742884, 215.57217382],
         [0, 0, 1]]

LeftDist=[0.09225191, -0.40577916, -0.00708927, -0.0050356, 0.5408364]

RightMat=[[590.61725106, 0, 288.20236937],
         [0, 589.41015463, 228.98459041],
         [0, 0, 1]]

RightDist=[0.05790892, -0.41533829, -0.00990576, -0.00553869, 3.12468689]
count=0
cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
if __name__ == '__main__':
    cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')

    while True:
        if not (left.grab() and right.grab()):
            print("No more frames")
            break

        _, leftFrame = left.retrieve()
        _, rightFrame = right.retrieve()

        cv2.imshow('left', leftFrame)
        cv2.imshow('right', rightFrame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    left.release()
    right.release()
    cv2.destroyAllWindows()

        '''
        #get image, split and assign to left and right
        ret, img = cap.read()
        
        img1 = img[0:480,  0:640]       #left
        img2 = img[0:480,  640:1280]   #right
        #cv2.imshow("Left", img1)
        #cv2.imshow("Right", img2)
        singleL=cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        singleR=cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        cv2.waitKey()

        stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
        disparity = stereo.compute(singleL,singleR)
        plt.imshow(disparity,'gray')
        plt.show()
        cv2.waitKey()
        cv2.destroyAllWindows()
        count+=1
        https://albertarmea.com/post/opencv-stereo-camera/
    '''
        
        
