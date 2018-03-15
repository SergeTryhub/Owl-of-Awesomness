#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#-----------------------------
import numpy as np
import socket
import cv2
import StringIO
import time
import keyboard


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
#s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
#data = s.recv(BUFFER_SIZE)
#s.close()
#---------------------------
# local modules
from common import clock, draw_str
from video import create_capture
#camera sourse
video_src = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
ret, img = video_src.read()

#left+right and centres of the images
left = img[0:480,  0:640]
Lcam_cx = 240
Lcam_cy = 320
right = img[0:480,  640:1280]
Rcam_cx = 240
Rcam_cy = 320

#face centers
Lface_cx = Lcam_cx
Lface_cy = Lcam_cy
Rface_cx = Rcam_cx
Rface_cy = Lcam_cy

#motion center points
Rpan_cx = RxC
Rpan_cy = RyC
Lpan_cx = LxC
Lpan_cy = LyC

#amount to move for each servo
Rmove_x = 10
Rmove_y = 10
Lmove_x = 10
Lmove_y = 10

#timers in seconds, local + wide
face_time1 = 10
face_time2 = 20

#stop lookinh if its too long
face_time3 = 30
pan_park = False


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def pan_fry(RyC,RxC,LyC,LxC):
    if (RyC>2000):
        RyC = 2000
    if (RyC<1120):
        RyC = 1120
    if (RxC>1890):
        RxC = 1890
    if (RxC<1200):
        RxC = 1200
    if (LyC>2000):
        LyC = 2000
    if (LyC<1180):
        LyC = 1180
    if (LxC>1850):
        LxC = 1850
    if (LxC<1180):
        LxC = 1180

#s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))

R_limit_y_bottom = 2000
R_limit_y_top = 1120
#R_limit_y_level = 
R_limit_x_left = 1200
R_limit_x_right = 1890

L_limit_y_bottom = 2000
L_limit_y_top = 1180
#L_limit_y_level = 
L_limit_x_left = 1180
L_limit_x_right = 1950

if __name__ == '__main__':
    import sys, getopt
    print(__doc__)

    args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
    try:
        #vidoe_src = video_src[0]
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
    pan_fry(RyC,RxC,LyC,LxC)
    face_found = False
    start_time = time.time()
    
    while True:        
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        t = clock()
        rects = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))#green color big rect
        #-------------------------------------------------------
        for x1, y1, x2, y2 in rects:
            if x2>0:
                face_found = True
                pan_parked = False
                start_time = time.time
            Rface_cx = x1 + x2/2
            Rnav_LR = Rcam_cx - Rface_cx
            Rpan_cx = Rpan_cx - Rnav_LR/5

            Rface_cy = y1 + y2/2
            Rnav_UD = Rcam_cy - Rface_cy
            Rpan_cy = Rpan_cy - Rnav_UD/5
        #---------------------------------------------------------
            Lface_cx = x1 + x2/2
            Lnav_LR = Lcam_cx - Lface_cx
            Lpan_cx = Lpan_cx - Lnav_LR/5

            Lface_cy = y1 + y2/2
            Lnav_UD = Lcam_cy - Lface_cy
            Lpan_cy = Lpan_cy - Lnav_UD/5
            #print ('R_Nav LR=%s UD=%s' % (Rnav_LR, Rnav_UD))
            #print ('L_Nav LR=%s UD=%s' % (Lnav_LR, Lnav_UD))
            
        '''if not nested.empty():
            for x1, y1, x2, y2 in rects:
                roi = gray[y1:y2, x1:x2]
                vis_roi = vis[y1:y2, x1:x2]
                subrects = detect(roi.copy(), nested)
                draw_rects(vis_roi, subrects, (255, 0, 0))#blue color two small rect'''
        elapsed_time = time.time() - time.time()#start_time
        #start pan/tils stuff
        if elapsed_time > face_time3:
            if not pan_parked:
                pan_fry(Rpan_cx, Rpan_cy)
                print('Waiting for face...')
                pan_parked = True

        elif elapsed_time > face_time2:
            face_found = False
            print('Wide search Timer2%d > %s seconds' % (elapsed_time, face_time2))
            Rpan_cx = Rpan_cx + Rmove_x
            Lpan_cx = Lpan_cx + Lmove_x
            if Rpan_cx > R_limit_x_right:
                 Rpan_cx = R_limit_x_left
                 Rpan_cy = Rpan_cy + Rmove_y
                 if Rpan_cy > R_limit_y_top:
                    Rpan_cy = R_limit_y_bottom
            pan_fry(RyC,RxC,LyC,LxC)
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
              
            if Lpan_cx > L_limit_x_right:
                 Lpan_cx = L_limit_x_left
                 Lpan_cy = Lpan_cy + Lmove_y
                 if Lpan_cy > L_limit_y_top:
                    Lpan_cy = L_limit_y_bottom
            pan_fry(RyC,RxC,LyC,LxC)
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))

        elif elapsed_time > face_time1:
            face_found = False
            print('Local search Timer1=%d > %s seconds' % (elapsed_time, face_time1))
            Rpan_cx = Rpan_cx + Rmove_x
            Lpan_cx = Lpan_cx + Lmove_x
            if Rpan_cx > R_limit_x_right:
                 Rpan_cx = R_limit_x_left
                 Rpan_cy = Rpan_cy + Rmove_y
                 if Rpan_cy > R_limit_y_top:
                    Rpan_cy = R_limit_y_bottom
            pan_fry(RyC,RxC,LyC,LxC)
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
              
            if Lpan_cx > L_limit_x_right:
                 Lpan_cx = L_limit_x_left
                 Lpan_cy = Lpan_cy + Lmove_y
                 if Lpan_cy > L_limit_y_top:
                    Lpan_cy = L_limit_y_bottom
            pan_fry(RyC,RxC,LyC,LxC)
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
        
        dt = clock() - t

        draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
        cv2.imshow('facedetect', vis)

        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()
