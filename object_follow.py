#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#-----------------------------
import socket
import cv2
import StringIO
import time
import numpy as np
import math
import sys
from matplotlib import pyplot as plt
from common import clock, draw_str
from video import create_capture
from random import randint


TCP_IP = '10.0.0.10'
TCP_PORT = 12345
BUFFER_SIZE = 24
#centerpoints for servos
RxC=1460
LxC=1540
RyC=1560
LyC=1470
NeckC =1480

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

Rx = RxC
Ry = RyC
Lx = LxC
Ly = LyC
Neck = NeckC
s.send('{} {} {} {} {}'.format(Rx, Ry, Lx, Ly, Neck))

#camera sourse
video_src = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
ret, img = video_src.read()

#left+right and centres of the images
left = img[0:480, 0:640]
right = img[0:480, 640:1280]
Lcam_x = 320#mid screen pos
Lcam_y = 240
Rcam_x = 320
Rcam_y = 240
midWindow = 15
ObjectL=None
ObjectR=None

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
# dealing with previous versions of open cv
def tracking(img,  eye):
    global right, left, trackerR, trackerL, trk_type, rectR, rectL
    
    trk_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW'] # need to decide on best tracker to use
    trk_type = trk_types[0]
    rectR = np.matrix('')
    rectL = np.matrix('')
    if int(major_ver) > 3:
        tracker = cv2.Tracker_create(trk_type)
    else:
        if trk_type == 'BOOSTING':
            trackerR = cv2.TrackerBoosting_create()
            trackerL = cv2.TrackerBoosting_create()
        if trk_type == 'MIL':
            trackerR = cv2.TrackerMIL_create()
            trackerL = cv2.TrackerMIL_create()
        if trk_type == 'KCF':
            trackerR = cv2.TrackerKCF_create()
            trackerL = cv2.TrackerKCF_create()
        if trk_type == 'TLD':
            trackerR = cv2.TrackerTLD_create()
            trackerL = cv2.TrackerTLD_create()
        if trk_type == 'MEDIANFLOW':
            trackerR = cv2.TrackerMedianFlow_create()
            trackerL = cv2.TrackerMedianFlow_create()
            
    #selecting a region of interest
    if eye == 'right':
        rect = cv2.selectROI(img, False)
        rectR = rect
        print ('RIGHT:',rectR)
    elif eye == 'left':
        rect = cv2.selectROI(img, False)
        rectL = rect        
        print ('LEFT:',rectL)
        
    okR = trackerR.init(img, rect)
    okL = trackerL.init(img, rect)
    cv2.destroyAllWindows()
    

def next_frame(img, eye):
    global rectL, rectR
    timer=cv2.getTickCount()
    if eye=='left':
        okL, rect=trackerL.update(img)
        x1=int(rect[0])
        y1=int(rect[1])
        x2=int(rect[2])
        y2=int(rect[3])
        rectL=(x1, y1, x2, y2)
        print('L is',rectL)
        if okL:
            p1=(int(rectL[0]),int(rectL[1]))
            p2=(int(rectL[0])+(rectL[2]), int(rectL[1]+rectL[3]))
            cv2.rectangle(img, p1, p2, (0,255,0), 2, 1)
        else:
            cv2.putText(img, "warning...WARNING!", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    elif eye=='right':
        okR, rect=trackerR.update(img)
        x1=int(rect[0])
        y1=int(rect[1])
        x2=int(rect[2])
        y2=int(rect[3])
        rectR=(x1, y1, x2, y2)
        print('R is',rectR)
        if okR:
            p1=(int(rectR[0]),int(rectR[1]))
            p2=(int(rectR[0])+(rectR[2]), int(rectR[1]+rectR[3]))
            cv2.rectangle(img, p1, p2, (0,255,0), 2, 1)
        else:
            cv2.putText(img, "warning...WARNING!", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    
def search():
    global Neck
    Neck = randint(1110, 1940)
            
def track():
    global Rx, Ry, Lx, Ly, Neck, ObjectL, ObjectR
    #----------------------
    x1L=rectR[0]
    y1L=rectR[1]
    x2L=rectR[2]
    y2L=rectR[3]
    #----------------------
    ObjectLx=x1L+((x2L)/2)
    ObjectLy=y1L+((y2L)/2)
    ObjectL=[ObjectLx, ObjectLy]
    #ALSO
    x1R=rectR[0]
    y1R=rectR[1]
    x2R=rectR[2]
    y2R=rectR[3]    
    #-------------------------
    ObjectRx=x1R+((x2R)/2)
    ObjectRy=y1R+((y2R)/2)
    ObjectR=[ObjectRx, ObjectRy]

    if (ObjectL != [0 , 0]):
        if(ObjectLx <(Lcam_x-midWindow)):
            Lx+=15
        elif(ObjectLx >(Lcam_x+midWindow)):
            Lx-=5

        if(ObjectLy <(Lcam_y-20)):
            Ly-=5
        elif(ObjectLy >(Lcam_y+20)):
            Ly+=5

    if (ObjectR !=[0 , 0]):#np.any
        if(ObjectRx <(Rcam_x-midWindow)):
            Rx+=15
        elif(ObjectLx >(Lcam_x+midWindow)):
            Rx-=5

        if(ObjectRy <(Rcam_y-20)):
            Ry+=5
        elif(ObjectLy >(Lcam_y+20)):
            Ry-=5

    if  Lx < 1200:
        Neck+=20
    elif  Lx > 1800:
        Neck-=20
    if np.any(ObjectL and ObjectR == None):
        print('ooops, we seem to have missed it')
        search()
    else:
        pass

if __name__ == '__main__':
    import sys, getopt
    ret, img=video_src.read()
    left = img[0:480, 0:640]
    right = img[0:480, 640:1280]
    tracking(left, 'left')
    #tracking(right, 'right')


    #cam = create_capture(video_src, fallback='synth:bg=../data/lena.jpg:noise=0.05')
    #cam = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')

    while True:        
        ret, img = video_src.read()
        left = img[0:480, 0:640]
        right = img[0:480, 640:1280]
        next_frame(left, 'left')
        next_frame(right, 'right')
        t = clock()
        track()
        s.send('{} {} {} {} {}'.format(Rx, Ry, Lx, Ly, Neck))
        
        dt = clock() - t

        cv2.imshow('Left Side', left)
        cv2.imshow('Right Side', right)
        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()

