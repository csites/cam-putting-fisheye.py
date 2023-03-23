# -*- coding: utf-8 -*-
import yaml
import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import glob
import configparser
import os

CHECKERBOARD = (8,6)

subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

_img_shape = None
_gray_shape = None
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('Calibrations/*.jpg')


for fname in images:
    img = cv2.imread(fname)
    if _img_shape == None:
        _img_shape = img.shape[:2]
    else:
        assert _img_shape == img.shape[:2], "All images must share the same size."

#    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#    _gray_shape = gray.shape[::-1]
#    cv2.imshow(f"Greyimage", gray)
#    cv2.waitKey(1)    
#    gray = np.uint8(gray)
    
    # Color-segmentation to get binary mask
    lwr = np.array([0, 0, 143])
    upr = np.array([179, 61, 252])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    msk = cv2.inRange(hsv, lwr, upr)
     
    # Extract chess-board
#   krn = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 15))
    dlt = cv2.dilate(msk, krn, iterations=9)
    res = 255 - cv2.bitwise_and(dlt, msk)
    _gray_shape = res.shape[::-1]
    
    # Displaying chess-board features
    res = np.uint8(res)
    res = cv2.bitwise_not(res)
    cv2.imshow(f"fname",res)
    cv2.waitKey(1)
    
    # Find the chess board corners
    # ret, corners = cv2.findChessboardCorners(res, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    ret, corners = cv2.findChessboardCorners(res, CHECKERBOARD, flags=cv2.CALIB_CB_EXHAUSTIVE)
    
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(res,corners,(3,3),(-1,-1),subpix_criteria)
        imgpoints.append(corners)
        print(corners)
    else:
        print(ret)
        
N_OK = len(objpoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]

rms, _, _, _, _ = \
    cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        _gray_shape,
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Found " + str(N_OK) + " valid images for calibration")
print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")
DIM=_img_shape[::-1]
balance=1
dim2=None
dim3=None


img1 = cv2.imread("db/image_1.jpg")

dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
if not dim2:
    dim2 = dim1
if not dim3:
    dim3 = dim1
scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

# This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
undistorted_img1 = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
undistorted_img = cv2.line(undistorted_img1, (0,239), (639, 239), (0,0,255), 1)

cv2.imshow("undistorted image", undistorted_img)
img2 = cv2.imread("db/image_1.jpg")
img2 = cv2.line(img2, (0,239), (639, 239), (0,0,255), 1)
img2 = cv2.line(img2, (10, 0), (10, 479), (0,0,255), 1)
img2 = cv2.line(img2, (629, 0), (629, 479), (0,0,255), 1)
cv2.imshow("original distorted image", img2)

data = {'dim1': dim1, 
        'dim2':dim2,
        'dim3': dim3,
        'K': np.asarray(K).tolist(), 
        'D':np.asarray(D).tolist(),
        'new_K':np.asarray(new_K).tolist(),
        'scaled_K':np.asarray(scaled_K).tolist(),
        'balance':balance}


# Write out a jsaon cablibration.
import json
with open("fisheye_calibration_data.json", "w") as f:
    json.dump(data, f)
    
# Create an entry in ../config.ini 
# Note. This assume the application is one directory below where the config.ini is located.   
config = configparser.ConfigParser()
config.add_section('fisheye')
config.set('fisheye', 'K', str(K))
config.set('fisheye', 'D', str(D))
config.set('fisheye', 'Scaled_K', str(scaled_K))
osFilename=os.path.join(os.pardir, 'config.ini')
with open(osFilename, 'w') as config_file:
    config.write(config_file)
    
cv2.waitKey(0)
cv2.destroyAllWindows()


