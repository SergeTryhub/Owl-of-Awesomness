# Servo Control
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
NeckC =1530
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
idx=0
while True:
    cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
    ret, img = cap.read()
    cv2.imshow("image", img)
    left = img[0:480,  0:640]
    #cv2.imshow("cunt", left)
    right = img[0:480,  641:1280]
    #cv2.imshow("cunt2", right)
    cv2.waitKey(30)
    try:        
        if keyboard.is_pressed('w'):
            RyC=RyC+10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('a'):
            RxC=RxC+10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('s'):
            RyC=RyC-10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('d'):
            RxC=RxC-10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        #######################--THE OTHER SIDE--#########################
        elif keyboard.is_pressed('up'):
            LyC=LyC-10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('left'):
            LxC=LxC+10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('down'):
            LyC=LyC+10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('right'):
            LxC=LxC-10
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.05)
        elif keyboard.is_pressed('esc'):
            cv2.destroyAllWindows()
            break
        #######################--IMAGE CAPTURE--#########################
        elif keyboard.is_pressed('g'):
            
            imgName1="K:/OWL/Code/DATA/left_%i.jpg"%idx
            cv2.imwrite(imgName1, left)
        
            imgName2="K:/OWL/Code/DATA/right_%i.jpg"%idx
            cv2.imwrite(imgName2, right)
            idx=idx+1
        else:
            pass
    except:
        break

print('Bye, have a good day!!')




'''cnt=0
cnt2=0
while (cnt<5):
    RxC+=50
    LxC+=50    
    s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
    time.sleep(0.25)
    cnt+=1
    if (cnt==5):
        while(cnt2<5):        
            RxC-=50
            LxC-=50    
            s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))
            time.sleep(0.25)
            cnt2+=1


while s.recv(2) != 'ok':
    print ("waiting...")
 
#s.close()'''
