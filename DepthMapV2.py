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

def disp_map_color():
	global num_disp, disp, disp1, filteredImg
	num_disp = max_disp-min_disp
	
	stereoL = cv2.StereoSGBM_create(minDisparity = min_disp,
		numDisparities = num_disp,
		blockSize = block_Size,
		P1 = 8*3*window_size**2,
		P2 = 32*3*window_size**2,
		disp12MaxDiff = disp12,
		uniquenessRatio = unique,
		speckleWindowSize = specklesize,
		speckleRange = speckle_Range,
		preFilterCap = PFC, #63,
		mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
		)
	stereoR = cv2.ximgproc.createRightMatcher(stereoL)
	stereo = stereoL
	lmbda = 80000
	sigma = 1.2
	visual_multiplier = 1.0

	wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereoL)
	wls_filter.setLambda(lmbda)
	wls_filter.setSigmaColor(sigma)

	displ = stereoL.compute(unDistL, unDistR)  # .astype(np.float32)/16
	dispr = stereoR.compute(unDistR, unDistL)  # .astype(np.float32)/16
	displ = np.int16(displ)
	dispr = np.int16(dispr)
	filteredImg = wls_filter.filter(displ, unDistL, None, dispr)  # important to put "imgL" here!!!
	
	filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
	filteredImg = np.uint8(filteredImg)
	
	disp = stereo.compute(unDistR, unDistL).astype(np.float32) / 16
	#disp1 = stereo.compute(imgR, imgL).astype(np.float32) / 16
    

def nothing(x):
    pass

def image_process():
	global unDistL, unDistR, imgR, imgL
	ret, Frame = cap.read()
	imgR = rightFrame = Frame[0:480,  0:640]    #right eye
	imgL = leftFrame = Frame[0:480,  640:1280]  #left eye
	    
	#Undistort is increasing the distortion?
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
	
	#convert to greyscale
	#unDistRG=cv2.cvtColor(unDistR, cv2.COLOR_BGR2GRAY)
	#unDistLG=cv2.cvtColor(unDistL, cv2.COLOR_BGR2GRAY)
	

def create_window():
	global cap, img
	#cap = cv2.VideoCapture('/home/callum/opencv/ProjOwl/Owl.mp4')
	cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
	time.sleep(1)
	img = np.zeros((1,1,1), np.uint8)
	
	cv2.namedWindow('Disparity')
	cv2.namedWindow('Tools')
    
	cv2.createTrackbar('disp12MaxDiff', 'Tools', 57, 100, nothing)
	cv2.createTrackbar('uniquenessRatio', 'Tools', 2, 20, nothing)
	cv2.createTrackbar('speckleWindowSize', 'Tools', 0, 300, nothing)
	cv2.createTrackbar('blocksize', 'Tools', 5, 15, nothing)
	cv2.createTrackbar('speckle range', 'Tools', 2, 32, nothing)
	cv2.createTrackbar('window size', 'Tools', 3, 15, nothing)
	cv2.createTrackbar('min disp', 'Tools', 0, 15, nothing)
	cv2.createTrackbar('max disp', 'Tools', 10, 20, nothing)
	cv2.createTrackbar('preFilterCap', 'Tools', 63, 150, nothing)


def get_values():
	# get values from trackbars  
	global min_disp, max_disp, block_Size, speckle_Range, specklesize
	global window_size, disp12, unique, PFC

	min_disp = 16*cv2.getTrackbarPos('min disp', 'Tools') #16
	max_disp = 16*cv2.getTrackbarPos('max disp', 'Tools') #112
	BS = cv2.getTrackbarPos('blocksize', 'Tools') #16
	if BS % 2 == 0:
		BS += 1
	block_Size = BS
	speckle_Range = cv2.getTrackbarPos('speckle range', 'Tools') #32
	window_size = cv2.getTrackbarPos('window size', 'Tools')
	disp12 = cv2.getTrackbarPos('disp12MaxDiff', 'Tools')
	unique = cv2.getTrackbarPos('uniquenessRatio', 'Tools')
	specklesize = cv2.getTrackbarPos('speckleWindowSize', 'Tools')
	PFC = cv2.getTrackbarPos('preFilterCap', 'Tools')

if __name__ == '__main__':
	create_window()

	while True:
		image_process()
		get_values()
		disp_map_color()

		#cv2.imshow('Disparity undistorted', (disp-min_disp)/num_disp) #Colour
		cv2.imshow('Disparity no filter', (disp-min_disp)/num_disp) #Colour
		cv2.imshow('Disparity', filteredImg)
		cv2.imshow('Tools', img)
	   
		#print('finished loop')
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
    
	cv2.destroyAllWindows()
