#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
import socket
import StringIO
import time
import cv2
import sys, termios, tty, os

TCP_IP = '10.0.0.10'
TCP_PORT = 12345

BUFFER_SIZE = 24
 
RxC=Rx=1530 
RyC=Ry=1560
LxC=Lx=1420
LyC=Ly=1440 
NeckC=Neck=1530
button_delay = 0.2

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

def getch():  #capture the keyboard input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
 
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
 
print('Control the left camera using WASD and q for capture')
print('Control the right camera using UJHK and y for capture')
print('To exit press e') 


while True:

    cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
    ret, img = cap.read()
    cv2.imshow("image", img)
    cv2.waitKey(300)

    char = getch()
    servo='{} {} {} {} {}'.format(Rx, Ry, Lx, Ly, Neck)
    #print(servo)
    s.send(servo)
    if (char == "w"):
        #print("Left eye look up")
        Ly+=10
        time.sleep(button_delay)
 
    elif (char == "s"):
        #print("Left eye look down")
        Ly-=10
        time.sleep(button_delay)
 
    elif (char == "a"):
        #print("Left eye move right")
        Lx+=10
        time.sleep(button_delay)
 
    elif (char == "d"):
        #print("Left eye move left")
        Lx-=10
        time.sleep(button_delay)
 
    elif (char == "q"):
        print("Capture Left image")
        time.sleep(button_delay)

    elif (char == "u"):
        #print("Right eye look up")
        Ry+=10
        time.sleep(button_delay)
 
    elif (char == "j"):
        #print("Right eye look down")
        Ry-=10
        time.sleep(button_delay)
 
    elif (char == "h"):
        #print("Right eye move right")
        Rx+=10
        time.sleep(button_delay)
 
    elif (char == "k"):
        #print("Right eye move left")
        Rx-=10
        time.sleep(button_delay)
 
    elif (char == "y"):
        print("Capture Right image")
        time.sleep(button_delay)
 
    elif (char == "e"):
        print("Exit")
        cv2.destroyAllWindows()
        s.close()
        exit(0)