#!/usr/bin/env python
# Python 2/3 compatibility
from __future__ import print_function
#---------------------
#import socket
import cv2
import StringIO
import time
import glob
import keyboard
import numpy as np
from matplotlib import pyplot as plt

#TCP_IP = '10.0.0.10'
#TCP_PORT = 12345
#BUFFER_SIZE = 24
#s.close()

RxC=1460 
RyC=1560
LxC=1540
LyC=1470 
NeckC=1530
 
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((TCP_IP, TCP_PORT))
#s.send('{} {} {} {} {}'.format(RxC, RyC, LxC, LyC, NeckC))

#camera matrix
leftCameraMatrix=np.matrix('582.39100314 0 299.87247641; 0 581.86742884 215.57217382; 0 0 1')

leftDistortionCoefficients=np.matrix('0.09225191 -0.40577916 -0.00708927 -0.0050356 0.5408364')

rightCameraMatrix=np.matrix('590.61725106 0 288.20236937; 0 589.41015463 228.98459041; 0 0 1')

rightDistortionCoefficients=np.matrix('0.05790892 -0.41533829 -0.00990576 -0.00553869 3.12468689')

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''
def nothing(x):
    pass

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')

if __name__ == '__main__':
    cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
    time.sleep(1)
    
    cv2.namedWindow('Disparity')
    #cv2.createTrackbar('min disp', 'Disparity', 16, 30, nothing)
    #cv2.createTrackbar('max disp', 'Disparity', 128, 150, nothing)
    cv2.createTrackbar('blocksize', 'Disparity', 21, 30, nothing)
    cv2.createTrackbar('speckle range', 'Disparity', 16, 60, nothing)
    cv2.createTrackbar('window size', 'Disparity', 3, 16, nothing)
    
    while True:
        #print('in loop')
        
        ret, Frame = cap.read()
        imgR = rightFrame = Frame[0:480,  0:640]       #right eye
        imgL = leftFrame = Frame[0:480,  640:1280]   #left eye
        
        hR,  wR = imgR.shape[:2]
        newcameramtxR, roiR=cv2.getOptimalNewCameraMatrix(rightCameraMatrix,rightDistortionCoefficients,(wR,hR),0,(wR,hR))
        hL,  wL = imgL.shape[:2]
        newcameramtxL, roiL=cv2.getOptimalNewCameraMatrix(leftCameraMatrix,leftDistortionCoefficients,(wL,hL),0,(wL,hL))

        # undistort
        unDistL = cv2.undistort(imgL, leftCameraMatrix, leftDistortionCoefficients, None, newcameramtxL)
        unDistR = cv2.undistort(imgR, rightCameraMatrix, rightDistortionCoefficients, None, newcameramtxR)

        # crop the image
        xR,yR,wR,hR = roiR
        unDistR = unDistR[yR:yR+hR, xR:xR+wR]
        xL,yL,wL,hL = roiL
        unDistL = unDistL[yL:yL+hL, xL:xL+wL]
        
        # get values from trackbars  
        min_disp = 16 #cv2.getTrackbarPos('min disp', 'Disparity') #16
        max_disp = 112 #cv2.getTrackbarPos('max disp', 'Disparity') #112
        block_Size = cv2.getTrackbarPos('blocksize', 'Disparity') #16
        speckle_Range = cv2.getTrackbarPos('speckle range', 'Disparity') #32
        window_size = cv2.getTrackbarPos('window size', 'Disparity')
        
        num_disp = max_disp-min_disp
        
        stereo = cv2.StereoSGBM_create(minDisparity = min_disp,
            numDisparities = num_disp,
            blockSize = block_Size,
            P1 = 8*3*window_size**2,
            P2 = 32*3*window_size**2,
            disp12MaxDiff = 1,
            uniquenessRatio = 10,
            speckleWindowSize = 100,
            speckleRange = speckle_Range,
        )

        print('computing disparity...')
        #disp = stereo.compute(imgL, imgR).astype(np.float32) / 16
        disp = stereo.compute(unDistL, unDistR).astype(np.float32) / 16

        print('generating 3d point cloud...',)
        h, w = imgL.shape[:2]
        f = 0.8*w                          # guess for focal length
        Q = np.float32([[1, 0, 0, -0.5*w],
                        [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
                        [0, 0, 0,     -f], # so that y-axis looks up
                        [0, 0, 1,      0]])
        points = cv2.reprojectImageTo3D(disp, Q)
        colors = cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB)
        mask = disp > disp.min()
        out_points = points[mask]
        out_colors = colors[mask]
        out_fn = 'out.ply'
        write_ply('out.ply', out_points, out_colors)
        print('%s saved' % 'out.ply')

        #cv2.imshow('right', imgR)
        #cv2.imshow('left', imgL)
        #cv2.namedWindow('Disparity')
        cv2.imshow('Disparity', (disp-min_disp)/num_disp)
        #cv2.createTrackbar('window size', 'Disparity', 1, 10, window_size)
        #cv2.createTrackbar('min disp', 'Disparity', 1, 10, min_disp)
        #cv2.createTrackbar('max disp', 'Disparity', 1, 10, max_disp)

        

                
        #print('finished loop')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    
    cv2.destroyAllWindows()

'''(_, _, _, _, _, rotationMatrix, translationVector, _, _) = cv2.stereoCalibrate(
            objectPoints, leftImagePoints, rightImagePoints,
            leftCameraMatrix, leftDistortionCoefficients,
            rightCameraMatrix, rightDistortionCoefficients,
            imageSize, None, None, None, None,
            cv2.CALIB_FIX_INTRINSIC, TERMINATION_CRITERIA)

        (leftRectification, rightRectification, leftProjection, rightProjection,
            dispartityToDepthMap, leftROI, rightROI) = cv2.stereoRectify(
                leftCameraMatrix, leftDistortionCoefficients,
                rightCameraMatrix, rightDistortionCoefficients,
                imageSize, rotationMatrix, translationVector,
                None, None, None, None, None,
                cv2.CALIB_ZERO_DISPARITY, OPTIMIZE_ALPHA)

        leftMapX, leftMapY = cv2.initUndistortRectifyMap(
            leftCameraMatrix, leftDistortionCoefficients, leftRectification,
            leftProjection, imageSize, cv2.CV_32FC1)
        rightMapX, rightMapY = cv2.initUndistortRectifyMap(
            rightCameraMatrix, rightDistortionCoefficients, rightRectification,
            rightProjection, imageSize, cv2.CV_32FC1)

        np.savez_compressed(outputFile, imageSize=imageSize,
        leftMapX=leftMapX, leftMapY=leftMapY, leftROI=leftROI,
        rightMapX=rightMapX, rightMapY=rightMapY, rightROI=rightROI)


'''
