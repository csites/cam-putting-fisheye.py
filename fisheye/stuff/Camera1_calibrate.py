import numpy as np
import cv2

# Define the dimensions of the checkerboard
CHECKERBOARD_SIZE = (6, 4)
CHECKERBOARD = (4,6)
# Define the termination criteria for the iterative calibration algorithm
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
objp = np.zeros((CHECKERBOARD_SIZE[0] * CHECKERBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD_SIZE[0], 0:CHECKERBOARD_SIZE[1]].T.reshape(-1, 2)

# Arrays to store object points and image points from all calibration images
obj_points = []
img_points = []

# Load calibration images and find chessboard corners
for i in range(9):
    # Load image
    img = cv2.imread(f"image_{i+1}.jpg")

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)

    # Find chessboard corners
    # ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD_SIZE, None)

    # If corners are found, add object points and image points to the lists
    # if ret:
    #    obj_points.append(objp)
    #    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    #    img_points.append(corners)
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
        img_points.append(corners)
	###

# calculate K & D
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
N_imm = 9 # number of calibration images
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_imm)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_imm)]
retval, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
    obj_points,
    img_points,
    gray.shape[::-1],
    K,
    D,
    rvecs,
    tvecs,
    calibration_flags,
    (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))

# Calibrate the camera
# ret, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
#    obj_points, img_points, gray.shape[::-1], None, None
#)

# Print the distortion matrix and camera matrix
print("K matrix:")
print(K)
print("D matrix:")
print(D)

# In this script, we first define the dimensions of the checkerboard and the termination criteria for the iterative calibration algorithm. We then prepare object points, which are the coordinates of the corners of the checkerboard in the real world (in this case, we assume the corners are on a flat surface). We then load each calibration image and use OpenCV's findChessboardCorners function to detect the corners of the checkerboard in the image. If corners are detected, we add the object points and image points to separate lists.

#After loading all calibration images, we use OpenCV's fisheye.calibrate function to calibrate the camera. This function takes in the object points and image points, as well as the dimensions of the images, and returns the distortion matrix (D) and camera matrix (K), as well as the rotation and translation vectors for each calibration image.

#Finally, we print out the distortion and camera matrices.

#Note that the script assumes that the calibration images are named calibration1.jpg, calibration2.jpg, etc. and are located in the same directory as the script. You may need to adjust the code to match your specific filenames and file paths.
