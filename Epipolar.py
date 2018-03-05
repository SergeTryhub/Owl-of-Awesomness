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

#get image, split and assign to left and right
cap = cv2.VideoCapture('http://10.0.0.10:8080/stream/video.mjpeg')
ret, img = cap.read()
cv2.imshow("image", img)
img1 = img[0:480,  0:640]       #left
img2 = img[0:480,  640:1280]   #right
cv2.waitKey(30)

#camera matrix
LeftMat=[[582.39100314, 0, 299.87247641],
         [0, 581.86742884, 215.57217382],
         [0, 0, 1]]

LeftDist=[0.09225191, -0.40577916, -0.00708927, -0.0050356, 0.5408364]

RightMat=[[590.61725106, 0, 288.20236937],
         [0, 589.41015463, 228.98459041],
         [0, 0, 1]]

RightDist=[0.05790892, -0.41533829, -0.00990576, -0.00553869, 3.12468689]

sift = cv2.SIFT()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# FLANN parameters
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)

good = []
pts1 = []
pts2 = []

# ratio test as per Lowe's paper
for i,(m,n) in enumerate(matches):
    if m.distance < 0.8*n.distance:
        good.append(m)
        pts2.append(kp2[m.trainIdx].pt)
        pts1.append(kp1[m.queryIdx].pt)
        
pts1 = np.int32(pts1)
pts2 = np.int32(pts2)
F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_LMEDS)

# We select only inlier points
pts1 = pts1[mask.ravel()==1]
pts2 = pts2[mask.ravel()==1]

def drawlines(img1,img2,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2

# Find epilines corresponding to points in right image (second image) and
# drawing its lines on left image
lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1,1,2), 2,F)
lines1 = lines1.reshape(-1,3)
img5,img6 = drawlines(img1,img2,lines1,pts1,pts2)

# Find epilines corresponding to points in left image (first image) and
# drawing its lines on right image
lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
lines2 = lines2.reshape(-1,3)
img3,img4 = drawlines(img2,img1,lines2,pts2,pts1)

plt.subplot(121),plt.imshow(img5)
plt.subplot(122),plt.imshow(img3)
plt.show()
'''#undistort using matrix
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))
dstL = cv2.undistort(img, LeftMat, LeftDist, None, newcameramtx)

dstR = cv2.undistort(img, RightMat, RightDist, None, newcameramtx)'''
