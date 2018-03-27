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

# local modules
from common import clock, draw_str
from video import create_capture
#camera sourse
video_src = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
ret, img = video_src.read()

#left+right and centres of the images
#left = img[0:480,  0:640]
left = img[0:640,  0:480]
Lcam_x = 320#mid screen pos
Lcam_y = 240
#right = img[0:480,  640:1280]
right = img[640:1280,  0:480]
Rcam_x = 320
Rcam_y = 240
midWindow = 15
FaceL=None
FaceR=None



def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def face_search():
    global Neck
    Neck = randint(1110, 1940)

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.rectangle(img, (239, 319), (241, 321), color, 2)
        
def track():
    global Rx, Ry, Lx, Ly, Neck, FaceL, FaceR
    for x1, y1, x2, y2 in rects:
        FaceLx=x1+((x2-x1)/2)
        FaceLy=y1+((y2-y1)/2)
        FaceL=[FaceLx, FaceLy]
        #-------------------------
        FaceRx=x1+((x2-x1)/2)
        FaceRy=y1+((y2-y1)/2)
        FaceR=[FaceRx, FaceRy]

        if np.any(FaceL !=None):
            if(FaceLx <(Lcam_x-midWindow)):
                Lx+=15
            elif(FaceLx >(Lcam_x+midWindow)):
                Lx-=5

            if(FaceLy <(Lcam_y-20)):
                Ly-=5
            elif(FaceLy >(Lcam_y+20)):
                Ly+=5

        if np.any(FaceR !=None):
            if(FaceRx <(Rcam_x-midWindow)):
                Rx+=15
            elif(FaceLx >(Lcam_x+midWindow)):
                Rx-=5

            if(FaceRy <(Rcam_y-20)):
                Ry+=5
            elif(FaceLy >(Lcam_y+20)):
                Ry-=5

    if  Lx < 1200:
        Neck+=20
    elif  Lx > 1800:
        Neck-=20
    if np.any(FaceL and FaceR == None):
        face_search()
    else:
        pass

if __name__ == '__main__':
    import sys, getopt
    #print(__doc__)

    args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
    try:
        video_src = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
    except:
        video_src = 0
    args = dict(args)
    cascade_fn = args.get('--cascade', "../../data/haarcascades/haarcascade_frontalface_alt.xml")
    nested_fn  = args.get('--nested-cascade', "../../data/haarcascades/haarcascade_eye.xml")

    cascade = cv2.CascadeClassifier(cascade_fn)
    nested = cv2.CascadeClassifier(nested_fn)

    #cam = create_capture(video_src, fallback='synth:bg=../data/lena.jpg:noise=0.05')
    cam = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')

    while True:        
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        t = clock()
        rects = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))#green color big rect
            
        if not nested.empty():
            for x1, y1, x2, y2 in rects:
                roi = gray[y1:y2, x1:x2]
                vis_roi = vis[y1:y2, x1:x2]
                subrects = detect(roi.copy(), nested)
                draw_rects(vis_roi, subrects, (255, 0, 0))#blue color two small rect
        track()
        s.send('{} {} {} {} {}'.format(Rx, Ry, Lx, Ly, Neck))
        
        dt = clock() - t

        draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
        cv2.imshow('facedetect', vis)

        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()
