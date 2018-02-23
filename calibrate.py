#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2
import xml
import sys
import socket
from common import splitfn
import StringIO
import time
import cv2
import sys
import keyboard

# built-in modules
import os

if __name__ == '__main__':
    import sys
    import getopt
    from glob import glob

    args, img_mask = getopt.getopt(sys.argv[1:], '', ['debug=', 'square_size='])
    args = dict(args)
    args.setdefault('--debug', 'C:/Repository-OWL/Data/CalGood/output/')
    args.setdefault('--square_size', 1.0)
    if not img_mask:
        img_mask = 'C:/Repository-OWL/Data/CalGood/left*.jpg'  # default
    else:
        img_mask = img_mask[0]

    img_names = glob(img_mask)
    debug_dir = args.get('--debug')
    if not os.path.isdir(debug_dir):
        os.mkdir(debug_dir)
    square_size = float(args.get('--square_size'))

    pattern_size = (9, 6)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    obj_points = []
    img_points = []
    h, w = 0, 0
    img_names_undistort = []
    for fn in img_names:
        print('processing %s... ' % fn, end='')
        img = cv2.imread(fn, 0)
        if img is None:
            print("Failed to load", fn)
            continue

        h, w = img.shape[:2]
        found, corners = cv2.findChessboardCorners(img, pattern_size)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)

        if debug_dir:
            vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            path, name, ext = splitfn(fn)
            outfile = debug_dir + name + '_chess.png'
            cv2.imwrite(outfile, vis)
            if found:
                img_names_undistort.append(outfile)

        if not found:
            print('chessboard not found')
            continue

        img_points.append(corners.reshape(-1, 2))
        obj_points.append(pattern_points)

        print('ok')

    # calculate camera distortion
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)

    print("\nRMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: ", dist_coefs.ravel())
    #cv2.Save("Camera matrix.xml",camera_matrix)
    #cv2.Save("Distortion.xml",dist_coefs.ravel())
    #print('saved xml files')

    # undistort the image with the calibration
    print('')
    for img_found in img_names_undistort:
        img = cv2.imread(img_found)

        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        outfile = img_found + '_undistorted.png'
        print('Undistorted image written to: %s' % outfile)
        cv2.imwrite(outfile, dst)
        ################################################################
if __name__ == '__main__':
    import sys
    import getopt
    from glob import glob
    
    args1, img_mask1 = getopt.getopt(sys.argv[1:], '', ['debug=', 'square_size='])
    args1 = dict(args1)
    args1.setdefault('--debug', 'C:/Repository-OWL/Data/CalGood/output/')
    args1.setdefault('--square_size', 1.0)
    if not img_mask1:
        img_mask1 = 'C:/Repository-OWL/Data/CalGood/right*.jpg'  # default
    else:
        img_mask1 = img_mask1[0]

    img_names1 = glob(img_mask1)
    debug_dir = args.get('--debug')
    if not os.path.isdir(debug_dir):
        os.mkdir(debug_dir)
    square_size = float(args1.get('--square_size'))

    pattern_size = (9, 6)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    obj_points = []
    img_points = []
    h, w = 0, 0
    img_names_undistort = []
    for fn in img_names1:
        print('processing %s... ' % fn, end='')
        img = cv2.imread(fn, 0)
        if img is None:
            print("Failed to load", fn)
            continue

        h, w = img.shape[:2]
        found, corners = cv2.findChessboardCorners(img, pattern_size)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)

        if debug_dir:
            vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            path, name, ext = splitfn(fn)
            outfile = debug_dir + name + '_chess.png'
            cv2.imwrite(outfile, vis)
            if found:
                img_names_undistort.append(outfile)

        if not found:
            print('chessboard not found')
            continue

        img_points.append(corners.reshape(-1, 2))
        obj_points.append(pattern_points)

        print('ok')

    # calculate camera distortion
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)

    print("\nRMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: ", dist_coefs.ravel())

    # undistort the image with the calibration
    print('')
    for img_found in img_names_undistort:
        img = cv2.imread(img_found)

        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        outfile = img_found + '_undistorted.png'
        print('Undistorted image written to: %s' % outfile)
        cv2.imwrite(outfile, dst)

    cv2.destroyAllWindows()


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
